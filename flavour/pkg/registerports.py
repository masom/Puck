import os
import os.path
import subprocess
from collections import namedtuple
import rpm

Pkg = namedtuple("Pkg", ["portname", "name", "version", "release", "arch"])
Reader = namedtuple("Reader", ["template"])
Paths = namedtuple("Paths", ["specdir", "rpmdir"])

class Template(object):
    def __init__(self, content):
        self._content = content

    @staticmethod
    def resolve_variable(env, name):
        varname, sep, atts = name.partition('.')
        try:
            value =  env[varname.strip().lower()]
        except KeyError:
            errmsg = "Template uses unknown variable: {0}".format(varname)
            raise RuntimeError(errmsg)

        if not sep:
            return value

        for attribute in atts.split('.'):
            try:
                value = getattr(value, attribute)
            except AttributeError:
                errmsg = "object {0} missing attribute {1}"
                raise RuntimeError(errmsg.format(name, attribute))

        return value

    def render(self, **variables):
        sections = []
        remaining = self._content
        while remaining:
            prefix, sep, remaining = remaining.partition("%%")
            sections.append(prefix)
            if not sep:
                # no more variables to substitute
                break
            variable, sep, remaining = remaining.partition("%%")
            if not sep:
                raise RuntimeError("Improperly formatted template")

            value = self.resolve_variable(variables, variable)
            sections.append(str(value))

        return "".join(sections)

def build(pkg, template, paths):

    keys = dict(zip(pkg._fields, pkg))
    raw = subprocess.check_output(["pkg_info", "-f", pkg.portname])
    files = [ line[5:].strip() for line in raw.splitlines() if line.startswith('File:')]
    files = [ os.path.join('%{_bindir}', name[4:])
                for name in files if name.startswith('bin/')]

    install = [
            "mkdir -p $RPM_BUILD_ROOT%{_bindir}",
            "mkdir -p $RPM_BUILD_ROOT%{_bindir}/db46",
            "mkdir -p $RPM_BUILD_ROOT%{_bindir}/lua51",
            "mkdir -p $RPM_BUILD_ROOT/usr/bin"
    ]
    install += ["touch $RPM_BUILD_ROOT%s" % name
                    for name in files]

    spec = template.render(
                files='\n'.join(files),
                install='\n'.join(install),
                **keys)



    specfile = os.path.join(paths.specdir, "%s.spec" % pkg.name)

    with open(specfile, 'w') as fp:
        fp.write(spec)

    os.system("rpmbuild -bb {specfile}".format(specfile=specfile))

    rpmname = "{name}-{version}-{release}.{arch}.rpm".format(**keys)

    rpmfile = os.path.join(paths.rpmdir, pkg.arch, rpmname)
    return rpmfile



def installPackages(pkgs, cfg):
    ts = rpm.ts()
    ts.setFlags(rpm.RPMTRANS_FLAG_JUSTDB)

    with open(cfg.template) as fp:
        spectemplate = fp.read()

    template = Template(spectemplate)
    paths = Paths(rpm.expandMacro('%_specdir'), rpm.expandMacro('%_rpmdir'))

    for pkg in pkgs:
        match = ts.dbMatch(rpm.RPMTAG_NAME, pkg.name)
        if len(match) == 0:
            rpmfile = build(pkg, template, paths)
            ts.addInstall(rpmfile, rpmfile, 'i')

    if ts.check():
        raise RuntimeError("This should not happen")
    ts.order()

    def runCallback(reason, amount, total, rpmfile, client_data):
        if reason == rpm.RPMCALLBACK_INST_OPEN_FILE:
            client_data[rpmfile] = os.open(rpmfile, os.O_RDONLY)
            return client_data[rpmfile]
        elif reason == rpm.RPMCALLBACK_INST_CLOSE_FILE:
            os.close(client_data[rpmfile])

    result = ts.run(runCallback, {})

    if result:
        print("ERRORS")
        print(result)
    else:
        print("Packages")
        for te in ts:
            info = (te.N(), te.V(), te.R())
            print("name: %s version: %s release: %s" % info)
    ts.check()
    ts.verifyDB()

def main(fp, cfg):
    content = fp.read()
    fp.close()

    pkgs = (line.split()[0] for line in content.splitlines()
                              if line.strip())
    pkgs = ((rawname, rawname.rsplit('-', 1))
                        for rawname in pkgs)

    # Need to drop the commas in freebsd package versions
    pkgs = [Pkg(rawname, name, version.partition(',')[0], "1", "noarch")
                for rawname, (name, version) in pkgs]
    installPackages(pkgs, cfg)

if __name__ == "__main__":
    import sysconfig
    import os.path
    import sys
    data = sysconfig.get_path('data')
    hcndir = os.path.join(sysconfig.get_path('data'), 'share', 'hcn')

    reader = Reader(os.path.join(hcndir, "spectemplate"))

    main(sys.stdin, reader)



# sitelib for noarch packages, sitearch for others (remove the unneeded one)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}

Name:           Pixie
Version:        1.0
Release:        1%{?dist}
Summary:        Pixie, jail virtualization configuration client
Source0:        pixie-%{version}.tar.gz

License:	LGPL
BuildArch:      noarch

%description
Pixie is a FreeBSD jail virtualization configuration client. See http://github.com/masom/Puck

%prep
%setup -q


%build
# Remove CFLAGS=... for noarch packages (unneeded)
%{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

%files
%{_bindir}/pixie
%doc
# For noarch packages: sitelib
%{python_sitelib}/*
# For arch-specific packages: sitearch
%{python_sitearch}/*


%changelog

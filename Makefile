SERVER_PATH = ./server
SERVER_URL = http://puck:8080
PYTHON = python2.7

_PYTHON_DEPS = cherrypy mako python-novaclient
PYTHON_DEPS = $(foreach D, $(_PYTHON_DEPS), ${D}.pydep)

_DEPS = libapache2-mod-python python-pip python-sqlite
DEPS = $(foreach D, $(_DEPS), ${D}.dep)

puck: $(DEPS) $(PYTHON_DEPS) 
	@cd ${SERVER_PATH} && echo > puck.sqlite3 
	@cd ${SERVER_PATH} && cp puck.conf /etc/
	@cd ${SERVER_PATH} && python2.7 puck.py -c puck.conf -i 
	@echo "Run ${PYTHON} puck.py" 
	@echo "Browse to ${SERVER_URL}"

%.dep:
	apt-get install $*

%.pydep:
	${PYTHON} /usr/bin/easy_install $*

.PHONY: puck

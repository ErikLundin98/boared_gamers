DBDIR := db
VENVDIR = := venv

install_unix: 
	test -d $(DBDIR) || mkdir $(DBDIR)
	make install_packages

install_windows:
	if not exist "$(DBDIR)" mkdir $(DBDIR)
	make install_packages

install_packages:
	pip install -r requirements.txt
ROOT=.
WURFL_DATABASE=$(ROOT)/extras/wurfl-db/wurfl.xml

sdist: clean
	@echo
	@echo "> Creating Python source distribution package..."
	python setup.py sdist

	@echo
	@echo "> Source distribution package successfully generated in $(ROOT)/dist/"
	@echo

upload: clean
	@echo
	@echo "> Uploading Python source distribution package..."
	python setup.py register sdist upload
	@echo

dump: clean
	@echo
	@echo "> Building WURFL Python database module (tests/wurfl.py)..."
	@(\
		export PYTHONPATH=$PYTHONPATH:$(ROOT);\
		python wurfl_python/processor.py "$(WURFL_DATABASE)" --output "$(ROOT)/tests/wurfl.py" --group product_info;\
	)
	@echo
	@echo "> Building test UAs module (tests/uas.py)..."
	@(\
		php $(ROOT)/extras/scripts/dump.php > "$(ROOT)/tests/uas.py";\
	)
	@echo

clean:
	@echo
	@echo "> Cleaning up previously generated stuff..."
	@rm -f "$(ROOT)/tests/wurfl.py"
	@rm -f "$(ROOT)/tests/uas.py"
	@rm -rf "$(ROOT)/dist" "$(ROOT)/wurfl_python.egg-info"
	@find "$(ROOT)" -name "*.pyc" | xargs rm -f

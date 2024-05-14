python3 -m pip install --upgrade build
python3 -m pip install --upgrade twine

python3 -m build
twine upload -r pypicloud --verbose dist/*

rm -rf dist
rm -rf geo-helper.egg-info

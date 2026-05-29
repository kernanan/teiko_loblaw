setup:
	pip install -r requirements.txt

pipeline:
	python pipeline.py

dashboard:
	streamlit run dashboard.py --server.headless true

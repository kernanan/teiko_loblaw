setup:
	pip install -r requirements.txt
	plotly_get_chrome

pipeline:
	python pipeline.py

dashboard:
	streamlit run dashboard.py --server.headless true

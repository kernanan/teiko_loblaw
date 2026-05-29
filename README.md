Hi everyone! This is Kernan, I had a great time completing this assignment! Thank you for taking the time to review my work, and I hope we get the chance to talk soon :]


**INSTRUCTIONS:**

To run my program run the following 3 commands:

1. make setup
    - this will install the dependencies that are part of my project
2. make pipeline
    - this will populate the outputs/.. directory with all the boxplot.pngs and csv files you're probably looking for
3. make dashboard
    - if you'd like to see all this data in a web application
    - Note that I used streamlit for scopesake, building out an React/Angular frontend + API layer would also an option!


**DATABASE DESIGN: **

My SQL design is made up of two tables: Subjects and Samples.

Two main reasons why it was split this way:
1. Bob's overarching goal was to find whether a subject reacted to miraclib via blood samples.
2. Subject metadata like sex, condition,
and treatment are facts about a person that do not change between samples.

Given this, it made sense to create a 1 to many relationship between subject->*samples. Transforming the data this way segued nicely into the following steps, as there was a clear link between a subject to their blood's makeup (frequency table). Really, only a table join on the subject_id -> then a melt was needed (for reshaping). 

With this design, the following statistical analyses were possible with the same join (and just a few additional filtering/grouping).

**AREAS WHERE DATABASE DESIGN SCALES:**

If Bob wanted to run another round of samples, they would just get added to the sample table without schema changes. They would also map to their corresponding subjects neatly.

Vice versa if Bob wanted to add more subjects.

Even across 1000s of trials and millions of new samples, filter and join queries' runtime would run quickly.

**AREAS WHERE DATABASE DESIGN DOESN'T SCALE**

If Bob wanted to start tracking a sixth cell population, an ALTER TABLE would be needed to add a new column. This would leave NULLs on past data

The fix: it'd make sense to break samples into two different tables: samples and cellcounts. The sample table would have columns sample_id*, subject_id, time_from_treatment start. The cellcounts table would have sample_id, populationtype, and counts.

Pros: No alter tables to introduce new columns and NULL values. New cell populations would simply be a new row add in cellcounts.

Cons: more extra joins would have to be made to draw correlations

**CODE STRUCTURE:**

Since you (the grader) are the true end user, I structured my code to be as easy to grade as possible. With this it's also easily scalable/maintainable, as the following 4 files own respective responsibilities between:
1. data ingestion
2. data analysis
3. orchestration
4. UI

For grading purposes, most of the bulk is separated by function in analysis.py. Easily runnable with the "test_analysis_as_I_Code.py" file.

But here's the break down:

load_data.py
  Database initialization and CSV ingestion only. Turns given CSV in root into database design described above.

analysis.py
  Logic layer. Each step that Bob outlines for data analysis is it's own separate function.

  NOTE: statistical significance (p value of <.05) was factored in for comparisons. 

  Feel free to run the other test files as well.

pipeline.py
  Orchestration layer as per requurements to build DB, run analyses, and generate artifacts.

dashboard.py
  Streamlit UI only. Presentation layer in case you don't want to click through all 10 files manually.

If Bob were real, I would be interested in working iteratively with Bob to understand his work, then create a requirements/software off of his needs. It'd also give me a better idea of how to structure code to scale/maintain better. For now, the grader was my top priority.


**THANK YOU FOR YOUR TIME**

I'm very interested to get feedback from the team. I hope we can talk soon, thanks!

- Kernan

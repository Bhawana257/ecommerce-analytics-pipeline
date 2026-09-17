#  E-Commerce Analytics Pipeline



![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql)
![dbt](https://img.shields.io/badge/dbt-1.12-orange?logo=dbt)
![Airflow](https://img.shields.io/badge/Airflow-3.3.1-017CEE?logo=apacheairflow)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker)
![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-F2C811?logo=powerbi)

An end-to-end **e-commerce data engineering and analytics pipeline** that extracts data from an API, loads it into PostgreSQL, transforms it using dbt, validates data quality, orchestrates the workflow with Apache Airflow, and provides business insights through Power BI.

---

##  Project Overview

This project demonstrates how raw e-commerce data can be transformed into analytics-ready data through an automated data pipeline.

The pipeline follows an **ELT-style architecture**:

<img width="1919" height="1012" alt="image" src="https://github.com/user-attachments/assets/27cdf4d9-1a25-4ec6-b177-b44f7b505da2" />


```text
E-Commerce API
      ↓
Python API Ingestion
      ↓
PostgreSQL
      ↓
dbt Staging & Transformation
      ↓
dbt Data Quality Tests
      ↓
Analytics Models
      ↓
Power BI






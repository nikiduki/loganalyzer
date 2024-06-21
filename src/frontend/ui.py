import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from about import show_about_page

load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8000")


@st.cache_data(ttl=300)
def get_logs(skip=0, limit=100):
    '''Getting logs from the API.
       :param skip (int): Number of records to skip.
       :param limit (int): Maximum number of records to be returned.
       :return (pd.DataFrame): Dataframe with logs.
    '''
    try:
        response = requests.get(f"{API_URL}/logs/?skip={skip}&limit={limit}")
        response.raise_for_status()
        return pd.DataFrame(response.json())
    except requests.RequestException as e:
        st.error(f"Ошибка при получении логов: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def get_anomalous_logs(threshold=0.8, skip=0, limit=100):
    '''Getting anomalous logs from the API.
       :param threshold (float): Threshold value for defining an anomaly.
       :param skip (int): Number of records to skip.
       :param limit (int): Maximum number of records to be returned.
       :return (pd.DataFrame): Dataframe with anomalous logs.
    '''
    try:
        response = requests.get(f"{API_URL}/logs/anomalous/?threshold&skip={skip}&limit={limit}")
        response.raise_for_status()
        return pd.DataFrame(response.json())
    except requests.RequestException as e:
        st.error(f"Ошибка при получении аномальных логов: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def get_log_stats():
    '''Getting log statistics from API.
       :return (dict): Log statistics.
    '''
    try:
        response = requests.get(f"{API_URL}/logs/stats/")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Ошибка при получении статистики логов: {e}")
        return {}

def display_statistics(stats):
    '''Displaying statistics.
    '''
    st.header("Статистика")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Всего логов", stats.get("total_logs", 0))
    with col2:
        st.metric("Аномальные логи", stats.get("anomalous_logs", 0))
    with col3:
        st.metric("Процент аномалий", f"{stats.get('anomaly_percentage', 0):.2f}%")

def display_anomaly_chart(anomalous_logs):
    '''Displaying the anomaly chart.
    '''
    st.header("График аномалий")
    fig = px.scatter(anomalous_logs, x='timestamp', y='anomaly_score', color='server_id',
                     hover_data=['log_level', 'message'], title="Аномальные логи")
    st.plotly_chart(fig, use_container_width=True)

def display_log_level_distribution(anomalous_logs):
    '''Display the distribution of anomalies by log level.
    '''
    log_level_counts = anomalous_logs['log_level'].value_counts()
    fig_pie = px.pie(names=log_level_counts.index, values=log_level_counts.values,
                     title="Распределение аномалий по уровням логов")
    st.plotly_chart(fig_pie, use_container_width=True)

def display_anomalous_logs_table(anomalous_logs):
    '''Displaying the anoamly log table.
    '''
    st.header("Таблица аномальных логов")
    st.dataframe(anomalous_logs)

def main():
    '''Main function of Streamlit.
    '''
    st.set_page_config(page_title="Система обнаружения аномалий в логах", layout="wide")

    st.sidebar.title("Навигация")
    page = st.sidebar.radio("Выберите страницу", ["Главная", "О системе"])

    if page == "Главная":
        st.title("Система обнаружения аномалий в логах серверной архитектуры")

        stats = get_log_stats()
        anomalous_logs = get_anomalous_logs(threshold=anomaly_threshold)

        display_statistics(stats)
        display_anomaly_chart(anomalous_logs)
        display_log_level_distribution(anomalous_logs)
        display_anomalous_logs_table(anomalous_logs)

    elif page == "О системе":
        show_about_page()

if __name__ == "__main__":
    main()

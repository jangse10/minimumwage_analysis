import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# 1. 페이지 설정 및 DB 확인
st.set_page_config(page_title="최저임금 데이터 분석 대시보드", layout="wide")

DB_PATH = 'minimum_wage.db'

if not os.path.exists(DB_PATH):
    st.error(f"❌ '{DB_PATH}' 파일을 찾을 수 없습니다. 데이터베이스 파일이 같은 폴더에 있는지 확인해주세요.")
    st.stop()

# DB 연결 함수
def run_query(query):
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql(query, conn)

st.title("📊 대한민국 최저임금 및 영향력 분석")
st.markdown("최저임금 결정이 노동 시장에 미치는 영향을 시각적으로 분석합니다.")

# --- 차트 1: 연도별 최저임금 인상 추이 ---
st.header("1. 연도별 최저임금 인상 추이")
sql1 = "SELECT 연도, 시간급 FROM 최저임금 ORDER BY 연도"
df1 = run_query(sql1)

fig1 = px.bar(df1, x='연도', y='시간급', 
             title='연도별 최저임금 (원)',
             labels={'시간급': '시간급(원)'},
             text_auto=',.0f')
st.plotly_chart(fig1, use_container_width=True)

with st.expander("🔍 상세 정보 확인"):
    st.subheader("사용한 SQL")
    st.code(sql1, language='sql')
    st.subheader("인사이트")
    st.write("- 최저임금은 매년 꾸준히 상승하고 있으며, 특정 구간(예: 2018년)에서 큰 폭의 인상이 관찰됩니다.")
    st.write("- 시간급 1만원 시대에 가까워지는 추세를 한눈에 확인할 수 있습니다.")


# --- 차트 2: 최저임금 인상률 vs 미만율 변화 비교 ---
st.header("2. 최저임금 vs 미만율 변화 비교")
sql2 = """
SELECT a.연도, a.시간급, b.미만율_퍼센트
FROM 최저임금 a
JOIN 미만율 b ON CAST(a.연도 AS TEXT) = SUBSTR(b.적용시작일, 1, 4)
WHERE b.구분 = '경제활동인구부가조사기준'
ORDER BY a.연도
"""
df2 = run_query(sql2)

# 이중축 차트 생성
fig2 = make_subplots(specs=[[{"secondary_y": True}]])
fig2.add_trace(go.Scatter(x=df2['연도'], y=df2['시간급'], name="시간급(원)"), secondary_y=False)
fig2.add_trace(go.Scatter(x=df2['연도'], y=df2['미만율_퍼센트'], name="미만율(%)", line=dict(dash='dash')), secondary_y=True)

fig2.update_layout(title_text="최저임금과 미만율(최저임금보다 못 받는 근로자 비율) 추이")
fig2.update_yaxes(title_text="시간급 (원)", secondary_y=False)
fig2.update_yaxes(title_text="미만율 (%)", secondary_y=True)

st.plotly_chart(fig2, use_container_width=True)

with st.expander("🔍 상세 정보 확인"):
    st.subheader("사용한 SQL")
    st.code(sql2, language='sql')
    st.subheader("인사이트")
    st.write("- 미만율은 최저임금보다 낮은 임금을 받는 근로자의 비율을 나타냅니다.")
    st.write("- 최저임금이 급격히 오를 때 미만율도 동반 상승하는 경향이 있는지 분석해 볼 가치가 있습니다.")


# --- 차트 3: 연도별 최저임금 영향을 받는 근로자 비율 ---
st.header("3. 최저임금 영향률 변화")
sql3 = """
SELECT SUBSTR(적용시작일, 1, 4) AS 연도, 영향률_퍼센트
FROM 영향률
WHERE 구분 = '경제활동인구부가조사기준'
ORDER BY 연도
"""
df3 = run_query(sql3)

fig3 = px.bar(df3, x='연도', y='영향률_퍼센트', 
             title='최저임금 영향률 (%)',
             labels={'영향률_퍼센트': '영향률(%)'},
             color='영향률_퍼센트', color_continuous_scale='Reds')
st.plotly_chart(fig3, use_container_width=True)

with st.expander("🔍 상세 정보 확인"):
    st.subheader("사용한 SQL")
    st.code(sql3, language='sql')
    st.subheader("인사이트")
    st.write("- 영향률은 최저임금 인상으로 인해 임금이 올라가는 근로자의 비중을 뜻합니다.")
    st.write("- 특정 연도에 영향률이 높다는 것은 그만큼 최저임금 결정이 노동 시장에 미치는 파급력이 컸음을 의미합니다.")

st.info("💡 모든 차트는 마우스를 올리면 상세 수치를 볼 수 있으며, 우측 상단 도구로 확대/축소가 가능합니다.")
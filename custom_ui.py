import streamlit as st


def apply_custom_design():
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #F4F7FB;
            color: #243247;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #10243A, #183B56);
            min-width: 260px;
        }

        [data-testid="stSidebar"] * {
            color: #FFFFFF !important;
        }

        [data-testid="stSidebar"] p {
            color: #B9D0DF !important;
        }

        [data-testid="stSidebar"] [role="radiogroup"] {
            gap: 10px;
        }

        [data-testid="stSidebar"] [role="radio"] {
            background-color: rgba(255,255,255,0.07);
            padding: 12px 15px;
            border-radius: 10px;
            margin-bottom: 5px;
            border: 1px solid transparent;
        }

        [data-testid="stSidebar"] [role="radio"]:hover {
            background-color: #286B65;
        }

        [data-testid="stSidebar"] [role="radio"][aria-checked="true"] {
            background-color: #1BA784;
            border: 1px solid #64D9B5;
        }

        h1 {
            color: #17324D !important;
            font-weight: 750 !important;
        }

        h2, h3 {
            color: #244B63 !important;
            font-weight: 650 !important;
        }

        [data-testid="stMetric"] {
            background: #FFFFFF;
            padding: 22px;
            border-radius: 15px;
            border: 1px solid #E1EAF1;
            box-shadow: 0 3px 12px rgba(20,50,75,0.06);
        }

        [data-testid="stMetricLabel"] {
            color: #64748B !important;
        }

        [data-testid="stMetricValue"] {
            color: #137C70 !important;
            font-weight: 750;
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #FFFFFF;
            border-radius: 14px;
            border-color: #E1EAF1;
        }

        .stButton > button,
        .stDownloadButton > button {
            background: #168B78;
            color: white;
            border: none;
            border-radius: 9px;
            padding: 10px 22px;
            font-weight: 650;
            transition: 0.2s;
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover {
            background: #116B60;
            color: white;
            border: none;
        }

        .stTextInput input,
        .stTextArea textarea,
        .stNumberInput input,
        .stSelectbox div[data-baseweb="select"] {
            background-color: #FFFFFF;
            border-radius: 8px;
            border-color: #CBD8E3;
        }

        [data-testid="stDataFrame"] {
            border: 1px solid #E1EAF1;
            border-radius: 12px;
            overflow: hidden;
        }

        .stProgress > div > div > div {
            background-color: #1BA784;
        }

        hr {
            border-color: #DCE6EE;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def show_sidebar_branding():
    with st.sidebar:
        st.markdown(
            """
            <div style="padding:18px 5px 25px 5px;">
                <h1 style="color:#FFFFFF !important;
                           font-size:27px;
                           margin-bottom:4px;">
                    ◈ PlanRevive AI
                </h1>
                <p style="color:#B9D0DF;
                          font-size:12px;
                          margin-top:0;">
                    Intelligent Project Recovery
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )


def show_page_header(title, subtitle):
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(100deg,#FFFFFF,#EAF5F5);
            padding:24px 28px;
            border-radius:15px;
            border-left:5px solid #1BA784;
            margin-bottom:24px;
            box-shadow:0 3px 12px rgba(20,50,75,0.05);
        ">
            <h1 style="margin:0;color:#17324D;">{title}</h1>
            <p style="margin:7px 0 0 0;color:#64748B;">
                {subtitle}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

titanic = sns.load_dataset("titanic")

fig = plt.figure(figsize=(10, 4))
sns.countplot(x="class", data=titanic)

st.pyplot(fig)
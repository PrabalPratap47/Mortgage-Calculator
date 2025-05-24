import streamlit as st
import pandas as pd
import math
import plotly.graph_objects as go

st.title("🏡 Mortgage Repayments Calculator")

st.write("### 📊 Input Data")
col1, col2 = st.columns(2)
home_value = col1.number_input("Home Value ($)", min_value=0, value=500000)
deposit = col1.number_input("Deposit ($)", min_value=0, value=100000)
interest_rate = col2.number_input("Interest Rate (%)", min_value=0.0, value=5.5)
loan_term = col2.number_input("Loan Term (Years)", min_value=1, value=30)

# Calculate the repayments
loan_amount = home_value - deposit
monthly_interest_rate = (interest_rate / 100) / 12
number_of_payments = loan_term * 12

if monthly_interest_rate == 0:
    monthly_payment = loan_amount / number_of_payments
else:
    monthly_payment = (
        loan_amount
        * (monthly_interest_rate * (1 + monthly_interest_rate) ** number_of_payments)
        / ((1 + monthly_interest_rate) ** number_of_payments - 1)
    )

# Display the repayments
total_payments = monthly_payment * number_of_payments
total_interest = total_payments - loan_amount

st.write("### 💰 Repayments")
col1, col2, col3 = st.columns(3)
col1.metric(label="Monthly Repayments", value=f"${monthly_payment:,.2f}")
col2.metric(label="Total Repayments", value=f"${total_payments:,.2f}")
col3.metric(label="Total Interest", value=f"${total_interest:,.2f}")

# Create a data-frame with the payment schedule
schedule = []
remaining_balance = loan_amount

for i in range(1, int(number_of_payments) + 1):
    interest_payment = remaining_balance * monthly_interest_rate
    principal_payment = monthly_payment - interest_payment
    remaining_balance -= principal_payment
    remaining_balance = max(remaining_balance, 0)
    year = math.ceil(i / 12)

    schedule.append(
        [
            i,
            round(monthly_payment, 2),
            round(principal_payment, 2),
            round(interest_payment, 2),
            round(remaining_balance, 2),
            year,
        ]
    )

df = pd.DataFrame(
    schedule,
    columns=["Month", "Payment", "Principal", "Interest", "Remaining Balance", "Year"],
)

# Group data by year
yearly = df.groupby("Year").agg(
    {
        "Principal": "sum",
        "Interest": "sum",
        "Remaining Balance": "last",
    }
).reset_index()

# Plotly graph
fig = go.Figure()

fig.add_trace(go.Bar(x=yearly["Year"], y=yearly["Principal"], name="Principal Paid", marker_color="green"))
fig.add_trace(go.Bar(x=yearly["Year"], y=yearly["Interest"], name="Interest Paid", marker_color="red"))
fig.add_trace(go.Scatter(x=yearly["Year"], y=yearly["Remaining Balance"], name="Remaining Balance", mode="lines+markers", line=dict(color="blue", width=3)))

fig.update_layout(
    barmode="stack",
    title="Mortgage Repayment Breakdown by Year",
    xaxis_title="Year",
    yaxis_title="Amount ($)",
    legend_title="",
    template="plotly_white",
)

st.plotly_chart(fig, use_container_width=True)

# Show table
with st.expander("📄 View Full Payment Schedule"):
    st.dataframe(df.style.format({"Payment": "${:,.2f}", "Principal": "${:,.2f}", "Interest": "${:,.2f}", "Remaining Balance": "${:,.2f}"}))

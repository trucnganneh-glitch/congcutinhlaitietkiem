
import streamlit as st
import pandas as pd

st.image("logo.pjg", caption="Tiết kiệm thông minh", width=300)
# =========================
# CẤU HÌNH TRANG
# =========================
st.set_page_config(
    page_title="Tính lãi gửi tiết kiệm",
    page_icon="💰",
    layout="centered"
)

# =========================
# TIÊU ĐỀ
# =========================
st.title("💰 CÔNG CỤ TÍNH LÃI GỬI TIẾT KIỆM _ Nguyễn Trương Trúc Ngân")
st.caption("Công cụ tính toán tiền lãi tiền gửi ngân hàng")

st.divider()

# =========================
# HÀM ĐỊNH DẠNG TIỀN
# =========================
def format_vnd(amount):
    return f"{amount:,.0f} VNĐ".replace(",", ".")

# =========================
# NHẬP THÔNG TIN
# =========================
st.subheader("📋 Thông tin khoản tiền gửi")

with st.form("deposit_form"):
    principal = st.number_input(
        "Số tiền gửi (VNĐ)",
        min_value=100000,
        value=10000000,
        step=1000000,
        format="%d"
    )

    col1, col2 = st.columns(2)

    with col1:
        term = st.number_input(
            "Kỳ hạn (tháng)",
            min_value=1,
            max_value=120,
            value=12,
            step=1
        )

    with col2:
        annual_rate = st.number_input(
            "Lãi suất (%/năm)",
            min_value=0.0,
            max_value=30.0,
            value=5.0,
            step=0.1,
            format="%.2f"
        )

    interest_method = st.selectbox(
        "Hình thức nhận lãi",
        [
            "Cuối kỳ",
            "Hàng tháng",
            "Hàng quý"
        ]
    )

    submitted = st.form_submit_button(
        "🧮 TÍNH TIỀN LÃI",
        use_container_width=True
    )

# =========================
# TÍNH TOÁN
# =========================
if submitted:
    monthly_rate = annual_rate / 100 / 12

    if interest_method == "Cuối kỳ":
        total_interest = principal * annual_rate / 100 * term / 12
        periods = 1
        period_interest = total_interest
        period_label = "Cuối kỳ"

    elif interest_method == "Hàng tháng":
        periods = term
        period_interest = principal * monthly_rate
        total_interest = period_interest * periods
        period_label = "Tháng"

    else:  # Hàng quý
        periods = term // 3
        remainder = term % 3

        period_interest = principal * annual_rate / 100 * 3 / 12
        total_interest = period_interest * periods

        if remainder > 0:
            extra_interest = (
                principal * annual_rate / 100 * remainder / 12
            )
            total_interest += extra_interest

        period_label = "Quý"

    total_amount = principal + total_interest

    # =========================
    # HIỂN THỊ KẾT QUẢ
    # =========================
    st.divider()
    st.subheader("📊 Kết quả tính toán")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            label="💵 Tiền lãi định kỳ",
            value=format_vnd(period_interest)
        )

    with col2:
        st.metric(
            label="📈 Tổng tiền lãi",
            value=format_vnd(total_interest)
        )

    st.metric(
        label="🏦 Tổng gốc và lãi",
        value=format_vnd(total_amount)
    )

    st.caption(
        f"Tiền gốc: {format_vnd(principal)} | "
        f"Lãi suất: {annual_rate:.2f}%/năm"
    )

    # =========================
    # BẢNG LỊCH NHẬN LÃI
    # =========================
    st.divider()
    st.subheader("📅 Chi tiết lịch nhận lãi")

    schedule = []

    if interest_method == "Cuối kỳ":
        schedule.append({
            "Kỳ nhận lãi": f"Sau {term} tháng",
            "Tiền lãi (VNĐ)": total_interest,
            "Tiền gốc (VNĐ)": principal,
            "Tổng nhận (VNĐ)": total_amount
        })

    elif interest_method == "Hàng tháng":
        for i in range(1, periods + 1):
            is_last = i == periods
            schedule.append({
                "Kỳ nhận lãi": f"Tháng {i}",
                "Tiền lãi (VNĐ)": period_interest,
                "Tiền gốc (VNĐ)": principal if is_last else 0,
                "Tổng nhận (VNĐ)": (
                    period_interest + principal
                    if is_last else period_interest
                )
            })

    else:
        for i in range(1, periods + 1):
            is_last = (i == periods and remainder == 0)
            schedule.append({
                "Kỳ nhận lãi": f"Quý {i}",
                "Tiền lãi (VNĐ)": period_interest,
                "Tiền gốc (VNĐ)": principal if is_last else 0,
                "Tổng nhận (VNĐ)": (
                    period_interest + principal
                    if is_last else period_interest
                )
            })

        if remainder > 0:
            schedule.append({
                "Kỳ nhận lãi": f"Sau {term} tháng",
                "Tiền lãi (VNĐ)": (
                    principal * annual_rate / 100 * remainder / 12
                ),
                "Tiền gốc (VNĐ)": principal,
                "Tổng nhận (VNĐ)": (
                    principal * annual_rate / 100 * remainder / 12
                    + principal
                )
            })

    df = pd.DataFrame(schedule)

    # Định dạng bảng tiền tệ
    st.dataframe(
        df.style.format({
            "Tiền lãi (VNĐ)": "{:,.0f}",
            "Tiền gốc (VNĐ)": "{:,.0f}",
            "Tổng nhận (VNĐ)": "{:,.0f}"
        }),
        use_container_width=True,
        hide_index=True
    )

    # =========================
    # TẢI FILE EXCEL
    # =========================
    csv = df.to_csv(
        index=False,
        encoding="utf-8-sig"
    )

    st.download_button(
        label="📥 Tải bảng lịch nhận lãi (CSV)",
        data=csv,
        file_name="lich_nhan_lai.csv",
        mime="text/csv",
        use_container_width=True
    )

    st.info(
        "Lưu ý: Kết quả được tính theo lãi đơn, "
        "không tính lãi nhập gốc, thuế hoặc phí. "
        "Số tiền thực tế có thể khác tùy theo quy định "
        "và cách tính ngày của ngân hàng."
    )

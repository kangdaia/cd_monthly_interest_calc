import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import sys


def calculate_monthly_interest(file_path, loan_df):
    df_list = pd.read_excel(file_path, sheet_name="전세자금 입금내역")
    for idx, row in loan_df.iterrows():
        start_date, init_amount = row["입출금일"], row["지급금"]
        deposit_all_df = df_list[(df_list["대출건번호"] == idx)]
        deposit_main = deposit_all_df[deposit_all_df["항목"] == "상환금"]
        deposit_interest = deposit_all_df[deposit_all_df["항목"] == "이자"]

def process_excel(file_path, name):
    try:
        # 엑셀 파일 읽기
        df_full = pd.read_excel(file_path, 
                            sheet_name="전세자금 세부내역",
                            index_col='대출건 번호').iloc[1:]
        loans = df_full[df_full["조합원명"] == name]
        
        result = calculate_monthly_interest(file_path, loans)
        # result = df.select_dtypes(include=[int, float]).sum()
        
        # 결과를 메시지 박스로 표시
        messagebox.showinfo("Calculation Results", result)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def select_file(entry):
    file_path = filedialog.askopenfilename(
        title="Select Excel File",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )
    if file_path:
        entry.delete(0, tk.END)
        entry.insert(0, file_path)

def on_submit(file_entry, text_entry):
    file_path = file_entry.get()
    user_input = text_entry.get()
    if not file_path:
        messagebox.showerror("Error", "No file selected")
    else:
        process_excel(file_path, user_input)

def validate_numeric_input(char):
    return char.isdigit() or char == ''

def main():
    root = tk.Tk()
    root.title("전세자금대출 이자 계산기")

    # 파일 선택 관련 위젯
    tk.Label(root, text="전세자금대출 상환 파일:").grid(row=0, column=0, padx=10, pady=5)
    file_entry = tk.Entry(root, width=50)
    file_entry.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(root, text="찾아보기", command=lambda: select_file(file_entry)).grid(row=0, column=2, padx=10, pady=5)

    # 사용자 입력 관련 위젯
    tk.Label(root, text="조합원 이름:").grid(row=1, column=0, padx=10, pady=5)
    name_entry = tk.Entry(root, width=50)
    name_entry.grid(row=1, column=1, padx=10, pady=5)

    # 제출 버튼
    tk.Button(root, text="다음", command=lambda: on_submit(file_entry, name_entry)).grid(row=2, columnspan=3, pady=10)

    root.mainloop()

if __name__=="__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
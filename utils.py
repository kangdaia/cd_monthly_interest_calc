def get_month_diff(start, end):
    year_diff = end.year - start.year
    month_diff = end.month - start.month + (1 if end.day > start.day else 0) 
    return year_diff * 12 + month_diff
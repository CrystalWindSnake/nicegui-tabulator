from nicegui_tabulator import tabulator, use_theme
from nicegui import ui


use_theme("semanticui", shared=False)

columns = [{"title": f"col{i}", "field": f"col{i}"} for i in range(30)]
columns[0]["frozen"] = True  # type: ignore

tabledata = [
    {"id": i + 1, **{col["field"]: f"row{i+1}-{col['field']}" for col in columns}}
    for i in range(100)
]

langs = {
    "cn": {
        "pagination": {
            "page_size": "每页数量",
            "page_title": "显示页面",
            "first": "首页",
            "first_title": "第一页",
            "last": "末页",
            "last_title": "最后一页",
            "prev": "上一页",
            "prev_title": "上一页",
            "next": "下一页",
            "next_title": "下一页",
            "all": "全部",
            "counter": {
                "showing": "正在显示",
                "of": "共",
                "rows": "条记录",
                "pages": "页",
            },
        }
    }
}

table_config = {
    "rowHeader": True,
    "data": tabledata,
    # "layout": "fitDataFill",
    "maxHeight": "50vh",
    "columns": columns,
    "pagination": "local",
    "paginationSize": 6,
    "paginationSizeSelector": [3, 6, 8, 10],
    "movableColumns": True,
    "paginationCounter": "rows",
    "langs": langs,
    "locale": "cn",
}

tabulator(table_config)


if __name__ in {"__main__", "__mp_main__"}:
    ui.run()

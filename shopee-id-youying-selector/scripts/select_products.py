#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


DEFAULT_COLUMNS = [
    "产品名称",
    "产品链接",
    "站点",
    "类目",
    "月销量",
    "价格(IDR)",
    "评分",
    "是否Shopee Mall",
    "上架时间",
    "店铺名称",
    "筛选结果",
    "淘汰原因",
    "抓取日期",
]

PLACEHOLDER_CREDENTIAL_VALUES = {
    "YOUR_USERNAME",
    "YOUR_PASSWORD",
    "<username>",
    "<password>",
}


def normalize_text(value) -> str:
    if value is None:
        return ""
    return str(value)


def is_placeholder_credential(value) -> bool:
    if value is None:
        return False
    return str(value).strip() in PLACEHOLDER_CREDENTIAL_VALUES


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def detect_chrome_path(configured_path: str | None) -> str:
    candidates = []
    if configured_path:
        candidates.append(configured_path)

    env_candidates = [
        os.getenv("CHROME_PATH"),
        os.getenv("GOOGLE_CHROME_BIN"),
        os.getenv("CHROMIUM_PATH"),
    ]
    candidates.extend([path for path in env_candidates if path])
    candidates.extend(
        [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
        ]
    )

    for binary_name in ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser"]:
        resolved = shutil.which(binary_name)
        if resolved:
            candidates.append(resolved)

    seen: set[str] = set()
    for candidate in candidates:
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        if Path(candidate).exists():
            return candidate

    raise SystemExit(
        "未找到可用的 Chrome/Chromium。请通过 --chrome-path 或配置文件显式指定，"
        "或设置 CHROME_PATH / GOOGLE_CHROME_BIN / CHROMIUM_PATH。"
    )


def autosize_columns(ws) -> None:
    for column_cells in ws.columns:
        values = ["" if cell.value is None else str(cell.value) for cell in column_cells]
        width = min(max(len(value) for value in values) + 2, 80)
        ws.column_dimensions[column_cells[0].column_letter].width = width


def write_workbook(rows: list[dict], output_path: Path, summary: dict) -> None:
    ensure_parent_dir(output_path)
    wb = Workbook()
    ws = wb.active
    ws.title = "products"
    ws.append(DEFAULT_COLUMNS)
    for row in rows:
        ws.append([row.get(column, "") for column in DEFAULT_COLUMNS])
    autosize_columns(ws)

    summary_ws = wb.create_sheet("summary")
    summary_ws.append(["字段", "值"])
    for key, value in summary.items():
        summary_ws.append([key, json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else value])
    autosize_columns(summary_ws)
    wb.save(output_path)


def write_json(rows: list[dict], output_path: Path) -> None:
    ensure_parent_dir(output_path)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(rows, handle, ensure_ascii=False, indent=2)


def load_config(path: str | None) -> dict:
    if not path:
        return {}
    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise SystemExit("Config JSON must be an object.")
    return data


def build_page_results_script() -> str:
    return """
    async ({startDate, endDate, limit, minSold, minPrice, minRating, categoryKeyword, today, maxPages, requestRetryLimit, mallFilterMode, mallKeywords, mallExcludeKeywords}) => {
      const root = document.querySelector("#app").__vue__;
      let target = null;
      const seen = new Set();
      const walk = vm => {
        if (!vm || seen.has(vm) || target) return;
        seen.add(vm);
        if (Object.keys(vm).includes("getGoodsList")) {
          target = vm;
          return;
        }
        (vm.$children || []).forEach(walk);
      };
      walk(root);
      if (!target) {
        throw new Error("未找到商品搜索组件");
      }

      const categoryTree = await fetch(location.origin + "/category/shopee/Indonesia/data/category.json").then(r => r.json());
      const category = categoryTree.find(item => {
        const text = `${item.cname || ""} ${item.cnameCn || ""}`.toLowerCase();
        return text.includes(categoryKeyword.toLowerCase());
      });
      if (!category) {
        throw new Error("未找到目标类目: " + categoryKeyword);
      }

      const selected = [];
      let pageIndex = 1;
      let pagesFetched = 0;
      let scannedCount = 0;

      const looksLikeMall = item => {
        const haystack = `${item.shopName || ""} ${item.userName || ""} ${item.categoryStructure || ""}`.toLowerCase();
        const keywords = Array.isArray(mallKeywords) ? mallKeywords.map(x => String(x).toLowerCase()) : [];
        const excludeKeywords = Array.isArray(mallExcludeKeywords) ? mallExcludeKeywords.map(x => String(x).toLowerCase()) : [];
        const hasBlockedKeyword = keywords.some(keyword => keyword && haystack.includes(keyword));
        const hasExcludedKeyword = excludeKeywords.some(keyword => keyword && haystack.includes(keyword));

        if (mallFilterMode === "none") return false;
        if (mallFilterMode === "strict") {
          return haystack.includes("shopee mall");
        }
        if (mallFilterMode === "loose") {
          return hasBlockedKeyword || haystack.includes("official") || haystack.includes("mall");
        }
        if (mallFilterMode === "custom") {
          return hasBlockedKeyword && !hasExcludedKeyword;
        }
        return hasBlockedKeyword;
      };

      const buildPayload = index => {
        const payload = JSON.parse(JSON.stringify(target.search.params));
        Object.assign(payload, {
          approvedDateEnd: "",
          approvedDateStart: "",
          cids: [category.cid],
          country: 2,
          genTimeEnd: endDate,
          genTimeStart: startDate,
          index,
          isAd: "",
          isShopeeVerified: "",
          monthlySalesEnd: "",
          monthlySalesStart: "",
          notInTitle: "",
          notInTitleStatus: 1,
          orderColumn: "sold",
          pageSize: 20,
          priceEnd: "",
          priceStart: String(minPrice),
          ratingEnd: "",
          ratingStart: String(minRating),
          shipInfoShopLocation: "",
          shopInfoShopLocation: "",
          shopee_choice: 1,
          soldEnd: "",
          soldStart: String(minSold),
          sort: "DESC",
          title: "",
          titleStatus: 1,
          token: target.http.defaults.headers.common.token || target.search.params.token,
        });
        return payload;
      };

      const postWithRetry = async payload => {
        let lastError = null;
        for (let attempt = 1; attempt <= requestRetryLimit; attempt += 1) {
          try {
            const response = await target.http.post("/shopee/product/productList", payload);
            if (response?.data?.code === 1) {
              return response;
            }
            lastError = new Error("查询失败: " + JSON.stringify(response?.data || null));
          } catch (error) {
            lastError = error;
          }
          await new Promise(resolve => setTimeout(resolve, 500 * attempt));
        }
        throw lastError || new Error("查询失败");
      };

      while (selected.length < limit && pageIndex <= maxPages) {
        const response = await postWithRetry(buildPayload(pageIndex));
        const rows = Array.isArray(response.data.data) ? response.data.data : [];
        pagesFetched += 1;
        if (!rows.length) {
          break;
        }
        scannedCount += rows.length;

        for (const item of rows) {
          const isMall = looksLikeMall(item);
          if (isMall) continue;
          if ((item.rating || 0) < minRating) continue;
          if ((item.price || 0) < minPrice) continue;
          if ((item.sold || 0) < minSold) continue;
          if (!item.genTime || item.genTime < startDate || item.genTime > endDate) continue;

          const sellerName = item.shopName || item.userName || "";
          selected.push({
            "产品名称": item.title || "",
            "产品链接": `https://shopee.co.id/product/${item.shopId}/${item.pid}`,
            "站点": "印度尼西亚",
            "类目": item.categoryStructure || "Otomotif",
            "月销量": item.sold || 0,
            "价格(IDR)": item.price || 0,
            "评分": item.rating || 0,
            "是否Shopee Mall": "否",
            "上架时间": item.genTime || "",
            "店铺名称": sellerName,
            "筛选结果": "入选",
            "淘汰原因": "",
            "抓取日期": today,
          });

          if (selected.length >= limit) {
            break;
          }
        }

        pageIndex += 1;
      }

      return {
        categoryCid: category.cid,
        categoryName: category.cname,
        pagesFetched,
        scannedCount,
        rows: selected,
      };
    }
    """


def login(page, username: str, password: str) -> None:
    page.goto("https://www.youyingshuju.com/index.html#/", wait_until="domcontentloaded")
    page.locator('input[placeholder="手机号 / 企业子账号用户名"]').fill(username)
    page.locator('input[placeholder="密码"]').fill(password)
    page.locator(".login_but.login_but_dl").click()
    try:
        page.wait_for_url("**/youyingshopee/index.html#/shopee/productsearch", timeout=15000)
    except PlaywrightTimeoutError as exc:
        body_text = page.locator("body").inner_text(timeout=5000)
        raise SystemExit(f"登录失败，当前页面提示: {body_text[:200]}") from exc
    page.wait_for_timeout(3000)


def collect_once(page, args: argparse.Namespace) -> dict:
    return page.evaluate(
        build_page_results_script(),
        {
            "startDate": args.start_date,
            "endDate": args.end_date,
            "limit": args.limit,
            "minSold": args.min_monthly_sales,
            "minPrice": args.min_price,
            "minRating": args.min_rating,
            "categoryKeyword": args.category_keyword,
            "today": args.capture_date,
            "maxPages": args.max_pages,
            "requestRetryLimit": args.request_retry_limit,
            "mallFilterMode": args.mall_filter_mode,
            "mallKeywords": args.mall_keywords,
            "mallExcludeKeywords": args.mall_exclude_keywords,
        },
    )


def login_and_collect(args: argparse.Namespace) -> tuple[list[dict], dict]:
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=args.chrome_path,
            headless=not args.headed,
        )
        page = browser.new_page(viewport={"width": 1440, "height": 1200})
        login(page, args.username, args.password)
        last_error: Exception | None = None
        results = None
        for attempt in range(1, args.run_retry_limit + 1):
            try:
                results = collect_once(page, args)
                break
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                if attempt >= args.run_retry_limit:
                    browser.close()
                    raise SystemExit(f"查询失败，重试 {attempt} 次后仍未成功: {exc}") from exc
                login(page, args.username, args.password)
        browser.close()

    if results is None:
        raise SystemExit(f"查询失败: {normalize_text(last_error)}")
    rows = results["rows"]
    if len(rows) < args.limit:
        raise SystemExit(
            f"只找到 {len(rows)} 个符合条件的商品，少于目标 {args.limit} 个。"
            f" 类目={results['categoryName']}({results['categoryCid']}), 已抓取页数={results['pagesFetched']}"
        )
    summary = {
        "capture_date": args.capture_date,
        "start_date": args.start_date,
        "end_date": args.end_date,
        "limit": args.limit,
        "min_monthly_sales": args.min_monthly_sales,
        "min_price": args.min_price,
        "min_rating": args.min_rating,
        "category_keyword": args.category_keyword,
        "max_pages": args.max_pages,
        "request_retry_limit": args.request_retry_limit,
        "run_retry_limit": args.run_retry_limit,
        "mall_filter_mode": args.mall_filter_mode,
        "mall_keywords": args.mall_keywords,
        "mall_exclude_keywords": args.mall_exclude_keywords,
        "matched_category_cid": results["categoryCid"],
        "matched_category_name": results["categoryName"],
        "pages_fetched": results["pagesFetched"],
        "scanned_count": results["scannedCount"],
        "selected_count": len(rows),
    }
    return rows, summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Select Shopee Indonesia products from YouYing and export to Excel.")
    parser.add_argument("--config", help="Optional JSON config file for login, filters, and output settings.")
    parser.add_argument("--username", help="YouYing account username.")
    parser.add_argument("--password", help="YouYing account password.")
    parser.add_argument("--start-date", help="Listing start date, YYYY-MM-DD.")
    parser.add_argument("--end-date", help="Listing end date, YYYY-MM-DD.")
    parser.add_argument("--output", help="Output xlsx path.")
    parser.add_argument("--capture-date", default=str(date.today()), help="Export capture date written into the Excel rows.")
    parser.add_argument("--limit", type=int, default=10, help="Number of products to export.")
    parser.add_argument("--min-monthly-sales", type=int, default=50, help="Minimum monthly sales.")
    parser.add_argument("--min-price", type=int, default=80000, help="Minimum price in IDR.")
    parser.add_argument("--min-rating", type=float, default=4.7, help="Minimum rating.")
    parser.add_argument("--category-keyword", default="Otomotif", help="Category keyword to match in the Indonesia category tree.")
    parser.add_argument("--max-pages", type=int, default=25, help="Maximum API pages to scan before stopping.")
    parser.add_argument("--request-retry-limit", type=int, default=3, help="Retries for each product-list API request.")
    parser.add_argument("--run-retry-limit", type=int, default=2, help="Retries for the whole run, including re-login.")
    parser.add_argument(
        "--mall-filter-mode",
        choices=["strict", "loose", "custom", "none"],
        default="custom",
        help="How to filter Shopee Mall / Official style stores.",
    )
    parser.add_argument(
        "--mall-keywords",
        nargs="*",
        default=["mall", "official", "official shop"],
        help="Keywords used when mall-filter-mode=custom or loose.",
    )
    parser.add_argument(
        "--mall-exclude-keywords",
        nargs="*",
        default=[],
        help="Keywords that override custom mall filtering when present.",
    )
    parser.add_argument(
        "--chrome-path",
        help="Chrome/Chromium executable path for Playwright. If omitted, the script auto-detects a browser.",
    )
    parser.add_argument("--json-output", help="Optional JSON output path for the raw selected rows.")
    parser.add_argument("--headed", action="store_true", help="Run the browser in headed mode.")
    args = parser.parse_args()
    config = load_config(args.config)
    defaults = {
        action.dest: action.default
        for action in parser._actions
        if getattr(action, "dest", None) and action.dest != "help"
    }

    for key in [
        "username",
        "password",
        "start_date",
        "end_date",
        "output",
        "capture_date",
        "limit",
        "min_monthly_sales",
        "min_price",
        "min_rating",
        "category_keyword",
        "max_pages",
        "request_retry_limit",
        "run_retry_limit",
        "mall_filter_mode",
        "mall_keywords",
        "mall_exclude_keywords",
        "chrome_path",
        "json_output",
    ]:
        current_value = getattr(args, key, None)
        default_value = defaults.get(key)
        should_fill_from_config = current_value in (None, "")
        if isinstance(current_value, list) and current_value == default_value:
            should_fill_from_config = True
        elif current_value == default_value:
            should_fill_from_config = True
        if should_fill_from_config and key in config:
            setattr(args, key, config[key])

    if not args.username or is_placeholder_credential(args.username):
        args.username = os.getenv("YOUYING_USERNAME")
    if not args.password or is_placeholder_credential(args.password):
        args.password = os.getenv("YOUYING_PASSWORD")
    args.chrome_path = detect_chrome_path(args.chrome_path)

    if not args.username or not args.password or not args.start_date or not args.end_date or not args.output:
        raise SystemExit(
            "username, password, start-date, end-date, and output are required. "
            "Username/password can also come from YOUYING_USERNAME and YOUYING_PASSWORD."
        )
    return args


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    rows, summary = login_and_collect(args)
    write_workbook(rows, output_path, summary)
    if args.json_output:
        write_json(rows, Path(args.json_output))
    print(json.dumps({"output": str(output_path), "count": len(rows)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

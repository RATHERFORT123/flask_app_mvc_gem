# repositories/analytics_repository.py
from collections import Counter
from collections import defaultdict
from datetime import datetime
from sqlalchemy import extract
from sqlalchemy import func, extract, or_, cast, String

# from sqlalchemy import func, extract
from app.models.contract import Contract
from app import db
# ✅ DEFINE safe_to_str HERE (or import it)
def safe_to_str(value):
        if isinstance(value, str):
            return value.strip().lower()
        elif value is None:
            return ""
        elif isinstance(value, float):
            import math
            if math.isnan(value):
                return ""
            return str(int(value)) if value.is_integer() else str(value)
        else:
            return str(value).strip().lower()
from sqlalchemy import func, extract
from app.models.contract import Contract
from app import db
from sqlalchemy import func, extract, or_


class AnalyticsRepository:

    # -------------------------
    # APPLY FILTERS (FIXED)
    # -------------------------
    @staticmethod
    def apply_filters(query, filters):
        if filters.get("status"):
            query = query.filter(Contract.status == filters["status"])

        if filters.get("buying_mode"):
            query = query.filter(Contract.buying_mode == filters["buying_mode"])

        if filters.get("ministry"):
            query = query.filter(
                Contract.ministry.ilike(f"%{filters['ministry']}%")
            )

        if filters.get("date_from"):
            query = query.filter(Contract.contract_date >= filters["date_from"])

        if filters.get("date_to"):
            query = query.filter(Contract.contract_date <= filters["date_to"])

        if filters.get("min_total") is not None:
            query = query.filter(Contract.total >= filters["min_total"])

        if filters.get("max_total") is not None:
            query = query.filter(Contract.total <= filters["max_total"])

        # return query

        # if filters.get('brands'):
        #         brand_conditions = []
        #         for brand in filters['brands']:
        #             brand_conditions.append(
        #                 Contract.items[0]['brand'].astext == brand
        #             )
        #         query = query.filter(or_(*brand_conditions))
        if filters.get("brands"):
         brands = filters["brands"]
 
         brand_conditions = [
             cast(Contract.items, String).ilike(f'%\"brand\": \"{b}\"%')
             for b in brands
         ]
 
         query = query.filter(or_(*brand_conditions))
        return query
    # -------------------------
    # CONTRACTS BY STATUS
    # -------------------------
    @staticmethod
    def get_contracts_by_status(filters):
        query = db.session.query(
            Contract.status,
            func.count(Contract.id)
        )

        query = AnalyticsRepository.apply_filters(query, filters)

        query = query.group_by(Contract.status)

        return query.all()


    # -------------------------
    # VALUE OVER TIME
    # -------------------------
    @staticmethod
    def get_value_over_time(filters):
        month_expr = func.strftime('%Y-%m', Contract.contract_date)

        query = db.session.query(
            month_expr.label("date"),
            func.sum(Contract.total)
        )

        query = AnalyticsRepository.apply_filters(query, filters)

        query = query.group_by(month_expr).order_by(month_expr)

        return query.all()


    # -------------------------
    # TOP MINISTRIES
    # -------------------------
    @staticmethod
    def get_top_ministries(filters, limit=10):
        query = db.session.query(
            Contract.ministry,
            func.sum(Contract.total)
        )

        query = AnalyticsRepository.apply_filters(query, filters)

        query = query.group_by(Contract.ministry)\
                     .order_by(func.sum(Contract.total).desc())

        return query.limit(limit).all()


    # -------------------------
    # AVG BY BUYING MODE
    # -------------------------
    @staticmethod
    def get_avg_by_buying_mode(filters):
        query = db.session.query(
            Contract.buying_mode,
            func.avg(Contract.total)
        )

        query = AnalyticsRepository.apply_filters(query, filters)

        query = query.group_by(Contract.buying_mode)

        return query.all()


    # -------------------------
    # COUNT BY MONTH
    # -------------------------
    @staticmethod
    def get_count_by_month(filters):
        query = db.session.query(
            extract("year", Contract.contract_date).label("year"),
            extract("month", Contract.contract_date).label("month"),
            func.count(Contract.id)
        )

        query = AnalyticsRepository.apply_filters(query, filters)

        query = query.group_by("year", "month").order_by("year", "month")

        return query.all()



# ----------------------------------------------------------------------------------------------


# class AnalyticsRepository:


# from datetime import datetime

# class AnalyticsRepository:

    @staticmethod
    def compare_brands_monthwise(brand1, brand2, month):
    
        from datetime import datetime
    
        year, mon = map(int, month.split("-"))
    
        def compute(brand):
            orders = 0
            revenue = 0
            quantity = 0
    
            status_breakdown = {}
            buying_modes = {}
            categories = set()
    
            contracts = Contract.query.all()
    
            for c in contracts:
                if not c.contract_date:
                    continue
    
                if c.contract_date.year != year or c.contract_date.month != mon:
                    continue
    
                for item in c.items or []:
                    if not isinstance(item, dict):
                        continue
    
                    b = safe_to_str(item.get("brand"))
                    if b.lower() != brand.lower():
                        continue
    
                    orders += 1
                    revenue += float(c.total or 0)
                    quantity += int(item.get("ordered_quantity") or 0)
    
                    # Status
                    status = c.status or "Unknown"
                    status_breakdown[status] = status_breakdown.get(status, 0) + 1
    
                    # Buying mode
                    mode = c.buying_mode or "Unknown"
                    buying_modes[mode] = buying_modes.get(mode, 0) + 1
    
                    # Category
                    cat = safe_to_str(item.get("category_name"))
                    if cat:
                        categories.add(cat)
    
            avg_value = revenue / orders if orders else 0
    
            return {
                "name": brand,
                "orders": orders,
                "revenue": round(revenue, 2),
                "avg_order_value": round(avg_value, 2),
                "quantity_sold": quantity,
                "status_breakdown": status_breakdown,
                "buying_modes": buying_modes,
                "categories": list(categories)
                # ✅ models REMOVED
            }
    
        return {
            "brand_1": compute(brand1),
            "brand_2": compute(brand2)
        }
    


    


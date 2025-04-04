from nicegui import ui
from datetime import datetime, timedelta
from src.auth.auth_roles import require_permission, get_user
from src.db.database import SessionLocal
from src.db.models import NFTMint
from collections import Counter

@require_permission('approve_images')
def director_dashboard():
    session = SessionLocal()
    user = get_user()
    today = datetime.now().date()
    this_month = today.replace(day=1)

    # Data calculations
    all_mints = session.query(NFTMint).filter_by(role='director').all()
    total_minted = len(all_mints)
    minted_today = sum(1 for m in all_mints if m.minted_at.date() == today)
    minted_this_month = sum(1 for m in all_mints if m.minted_at.date() >= this_month)
    role_counts = Counter(m.role for m in session.query(NFTMint).all())

    # Minting Trend - Last 7 Days
    last_7_days = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
    mint_per_day = {d: 0 for d in last_7_days}
    for m in all_mints:
        if m.minted_at.date() in mint_per_day:
            mint_per_day[m.minted_at.date()] += 1

    # ───────────────────────────── UI Layout ─────────────────────────────
    with ui.column().classes('w-full items-center p-8 bg-gray-50'):
        with ui.row().classes('w-full justify-between items-center mb-6'):
            ui.label(f'🎯 Director Dashboard - {user["email"]}').classes('text-2xl font-bold text-blue-900')
            with ui.row().classes('gap-3'):
                ui.button('🖼️ Review Submissions', on_click=lambda: ui.navigate.to('/director/approval')) \
                    .classes('bg-green-100 text-green-800 px-4 py-2 rounded')
                ui.button('🕘 Minting History - Director', on_click=lambda: ui.navigate.to('/director/history')) \
                    .classes('bg-green-100 text-green-800 px-4 py-2 rounded')
                ui.button('🔒 Logout', on_click=lambda: ui.navigate.to('/')) \
                    .classes('bg-gray-500 text-white px-4 py-2 rounded')

        # 🔷 Summary Cards
        with ui.row().classes('w-full justify-around mb-8'):
            with ui.card().classes('bg-white shadow-lg p-6 rounded-xl w-1/4'):
                ui.label(f'🔢 Total NFTs Minted: {total_minted}').classes('text-lg text-blue-800 text-center')
            with ui.card().classes('bg-white shadow-lg p-6 rounded-xl w-1/4'):
                ui.label(f'📆 Minted This Month: {minted_this_month}').classes('text-lg text-green-800 text-center')
            with ui.card().classes('bg-white shadow-lg p-6 rounded-xl w-1/4'):
                ui.label(f'🕒 Minted Today: {minted_today}').classes('text-lg text-indigo-800 text-center')

        # 🔶 Charts Row
        with ui.row().classes('w-full gap-6'):
            # Bar Chart
            with ui.card().classes('w-1/3 p-4 bg-white shadow-md rounded-xl'):
                ui.label('📊 Mint Summary').classes('text-xl font-semibold mb-3')
                ui.echart({
                    'xAxis': {'type': 'category', 'data': ['Total', 'This Month', 'Today']},
                    'yAxis': {'type': 'value'},
                    'series': [{
                        'data': [total_minted, minted_this_month, minted_today],
                        'type': 'bar',
                        'itemStyle': {'color': '#3b82f6'},
                    }]
                }).classes('h-64 w-full')

            # Pie Chart
            with ui.card().classes('w-1/3 p-4 bg-white shadow-md rounded-xl'):
                ui.label('🧑‍🏭 Minted by Role').classes('text-xl font-semibold mb-3')
                ui.echart({
                    'tooltip': {'trigger': 'item'},
                    'series': [{
                        'name': 'Mints',
                        'type': 'pie',
                        'radius': '60%',
                        'data': [{'value': count, 'name': role.capitalize()} for role, count in role_counts.items()],
                    }]
                }).classes('h-64 w-full')

            # Line Chart
            with ui.card().classes('w-1/3 p-4 bg-white shadow-md rounded-xl'):
                ui.label('📈 7-Day Minting Trend').classes('text-xl font-semibold mb-3')
                ui.echart({
                    'xAxis': {
                        'type': 'category',
                        'data': [d.strftime('%b %d') for d in last_7_days]
                    },
                    'yAxis': {'type': 'value'},
                    'series': [{
                        'data': [mint_per_day[d] for d in last_7_days],
                        'type': 'line',
                        'smooth': True,
                        'lineStyle': {'width': 3}
                    }]
                }).classes('h-64 w-full')

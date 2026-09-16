import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import uuid

# ============================================================
# CONFIGURATION
# ============================================================

NUM_USERS = 60000
NUM_SESSIONS_AVG = 6
NUM_RESTAURANTS = 1000

START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2023, 12, 31)

DATA_DIR = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(__file__)
        )
    ),
    'data',
    'raw'
)

os.makedirs(DATA_DIR, exist_ok=True)

np.random.seed(42)


# ============================================================
# USERS
# ============================================================

def generate_users():

    print("Generating users...")

    user_ids = [
        str(uuid.uuid4())
        for _ in range(NUM_USERS)
    ]

    # Signup dates weighted towards the beginning
    # of the year
    days_in_year = (
        END_DATE - START_DATE
    ).days

    signup_days = (
        np.random.beta(
            a=2,
            b=5,
            size=NUM_USERS
        ) * days_in_year
    )

    signup_dates = [
        START_DATE + timedelta(days=float(d))
        for d in signup_days
    ]

    channels = np.random.choice(
        [
            'Organic',
            'Paid Search',
            'Social Media',
            'Referral'
        ],
        size=NUM_USERS,
        p=[0.4, 0.3, 0.2, 0.1]
    )

    platforms = np.random.choice(
        [
            'iOS',
            'Android',
            'Web'
        ],
        size=NUM_USERS,
        p=[0.5, 0.4, 0.1]
    )

    # App version tied to platform
    app_versions = []

    for platform in platforms:

        if platform == 'Web':

            app_versions.append('N/A')

        elif platform == 'iOS':

            app_versions.append(
                np.random.choice(
                    ['v2.0', 'v2.1', 'v2.2'],
                    p=[0.2, 0.5, 0.3]
                )
            )

        else:

            app_versions.append(
                np.random.choice(
                    ['v1.8', 'v1.9', 'v2.0'],
                    p=[0.1, 0.6, 0.3]
                )
            )

    cities = np.random.choice(
        [
            'New York',
            'Los Angeles',
            'Chicago',
            'Houston',
            'Miami'
        ],
        size=NUM_USERS,
        p=[0.3, 0.25, 0.2, 0.15, 0.1]
    )

    # Premium users generate more sessions
    is_premium = np.random.choice(
        [True, False],
        size=NUM_USERS,
        p=[0.15, 0.85]
    )

    df = pd.DataFrame({
        'user_id': user_ids,
        'signup_date': signup_dates,
        'acquisition_channel': channels,
        'platform': platforms,
        'app_version': app_versions,
        'city': cities,
        'is_premium': is_premium
    })

    df.to_csv(
        os.path.join(DATA_DIR, 'users.csv'),
        index=False
    )

    return df


# ============================================================
# RESTAURANTS
# ============================================================

def generate_restaurants():

    print("Generating restaurants...")

    restaurant_ids = [
        str(uuid.uuid4())
        for _ in range(NUM_RESTAURANTS)
    ]

    cuisines = np.random.choice(
        [
            'Italian',
            'Chinese',
            'Indian',
            'Mexican',
            'American',
            'Japanese',
            'Healthy'
        ],
        size=NUM_RESTAURANTS
    )

    avg_ratings = np.clip(
        np.random.normal(
            loc=4.2,
            scale=0.5,
            size=NUM_RESTAURANTS
        ),
        1.0,
        5.0
    ).round(1)

    price_tiers = np.random.choice(
        [
            '$',
            '$$',
            '$$$',
            '$$$$'
        ],
        size=NUM_RESTAURANTS,
        p=[0.3, 0.4, 0.2, 0.1]
    )

    cities = np.random.choice(
        [
            'New York',
            'Los Angeles',
            'Chicago',
            'Houston',
            'Miami'
        ],
        size=NUM_RESTAURANTS,
        p=[0.3, 0.25, 0.2, 0.15, 0.1]
    )

    df = pd.DataFrame({
        'restaurant_id': restaurant_ids,
        'cuisine_type': cuisines,
        'avg_rating': avg_ratings,
        'price_tier': price_tiers,
        'city': cities
    })

    df.to_csv(
        os.path.join(DATA_DIR, 'restaurants.csv'),
        index=False
    )

    return df


# ============================================================
# SESSIONS + EVENTS + ORDERS
# ============================================================

def generate_sessions_and_events(
    users_df,
    restaurants_df
):

    print("Generating sessions and events...")

    # --------------------------------------------------------
    # NUMBER OF SESSIONS PER USER
    # --------------------------------------------------------

    base_sessions = np.random.poisson(
        lam=NUM_SESSIONS_AVG,
        size=len(users_df)
    )

    premium_boost = (
        users_df['is_premium'].astype(int) * 3
    )

    num_sessions_per_user = (
        base_sessions + premium_boost
    )

    num_sessions_per_user = np.clip(
        num_sessions_per_user,
        1,
        50
    )

    user_indices = np.repeat(
        np.arange(len(users_df)),
        num_sessions_per_user
    )

    session_users = (
        users_df
        .iloc[user_indices]
        .reset_index(drop=True)
    )

    num_total_sessions = len(session_users)

    session_ids = [
        str(uuid.uuid4())
        for _ in range(num_total_sessions)
    ]

    # --------------------------------------------------------
    # SESSION TIMESTAMPS
    # --------------------------------------------------------
    #
    # IMPORTANT:
    # Use timedelta arithmetic instead of converting
    # timestamps into raw integer nanoseconds.
    #
    # This prevents incorrect dates such as 1970, 1984, etc.
    # --------------------------------------------------------

    signup_dates = pd.to_datetime(
        session_users['signup_date']
    )

    random_offsets = np.random.random(
        num_total_sessions
    )

    available_seconds = (
        pd.Timestamp(END_DATE)
        - signup_dates
    ).dt.total_seconds().to_numpy()

    session_start_offsets = (
        available_seconds * random_offsets
    )

    session_starts = (
        signup_dates.reset_index(drop=True)
        + pd.to_timedelta(
            session_start_offsets,
            unit='s'
        )
    )

    # Safety clamp:
    # Every session must be between signup date
    # and the end of 2023.

    session_starts = session_starts.clip(
        lower=pd.Timestamp(START_DATE),
        upper=pd.Timestamp(END_DATE)
    )

    sessions_df = pd.DataFrame({
        'session_id': session_ids,
        'user_id': session_users['user_id'].values,
        'session_start': session_starts,
        'device_type': session_users['platform'].values
    })

    # --------------------------------------------------------
    # FUNNEL PROGRESSION
    # --------------------------------------------------------

    rand_funnel = np.random.rand(
        num_total_sessions
    )

    has_search = (
        rand_funnel < 0.85
    )

    has_view = (
        has_search &
        (
            np.random.rand(num_total_sessions)
            < 0.75
        )
    )

    has_cart = (
        has_view &
        (
            np.random.rand(num_total_sessions)
            < 0.65
        )
    )

    has_checkout_start = (
        has_cart &
        (
            np.random.rand(num_total_sessions)
            < 0.70
        )
    )

    base_checkout_success = (
        has_checkout_start &
        (
            np.random.rand(num_total_sessions)
            < 0.85
        )
    )

    # --------------------------------------------------------
    # RCA ANOMALY INJECTION
    # --------------------------------------------------------
    #
    # Android + v1.9 + Chicago
    # checkout success intentionally reduced to ~72%.
    # --------------------------------------------------------

    is_anomaly_segment = (
        (session_users['platform'] == 'Android') &
        (session_users['app_version'] == 'v1.9') &
        (session_users['city'] == 'Chicago')
    )

    anomaly_success_mask = (
        np.random.rand(num_total_sessions)
        < 0.72
    )

    has_checkout_success = np.where(
        is_anomaly_segment & has_checkout_start,
        anomaly_success_mask,
        base_checkout_success
    )

    has_checkout_fail = (
        has_checkout_start &
        ~has_checkout_success
    )

    # --------------------------------------------------------
    # SESSION DURATION
    # --------------------------------------------------------

    durations_sec = (
        10
        + has_search * 30
        + has_view * 120
        + has_cart * 180
        + has_checkout_start * 60
        + has_checkout_success * 30
        + has_checkout_fail * 45
    )

    durations_sec = (
        durations_sec
        + np.random.randint(
            10,
            100,
            num_total_sessions
        )
    )

    sessions_df['session_end'] = (
        sessions_df['session_start']
        + pd.to_timedelta(
            durations_sec,
            unit='s'
        )
    )

    sessions_df.to_csv(
        os.path.join(DATA_DIR, 'sessions.csv'),
        index=False
    )

    # ========================================================
    # EVENTS
    # ========================================================

    def build_events(
        mask,
        event_name,
        time_offset_sec
    ):

        idx = np.where(mask)[0]

        if len(idx) == 0:
            return pd.DataFrame()

        return pd.DataFrame({
            'event_id': [
                str(uuid.uuid4())
                for _ in range(len(idx))
            ],

            'session_id':
                sessions_df['session_id'].values[idx],

            'user_id':
                sessions_df['user_id'].values[idx],

            'timestamp':
                sessions_df['session_start'].values[idx]
                + pd.to_timedelta(
                    time_offset_sec,
                    unit='s'
                ),

            'event_name':
                event_name
        })

    e_open = build_events(
        np.ones(
            num_total_sessions,
            dtype=bool
        ),
        'app_open',
        2
    )

    e_search = build_events(
        has_search,
        'search',
        15
    )

    e_view = build_events(
        has_view,
        'view_restaurant',
        45
    )

    e_cart = build_events(
        has_cart,
        'add_to_cart',
        120
    )

    e_chk_start = build_events(
        has_checkout_start,
        'checkout_start',
        200
    )

    e_chk_succ = build_events(
        has_checkout_success,
        'checkout_success',
        250
    )

    e_chk_fail = build_events(
        has_checkout_fail,
        'checkout_fail',
        260
    )

    events_df = pd.concat(
        [
            e_open,
            e_search,
            e_view,
            e_cart,
            e_chk_start,
            e_chk_succ,
            e_chk_fail
        ],
        ignore_index=True
    )

    events_df.sort_values(
        ['session_id', 'timestamp'],
        inplace=True
    )

    events_df.to_csv(
        os.path.join(DATA_DIR, 'events.csv'),
        index=False
    )

    print(
        f"Generated {len(sessions_df)} sessions "
        f"and {len(events_df)} events."
    )

    # ========================================================
    # ORDERS
    # ========================================================

    succ_idx = np.where(
        has_checkout_success
    )[0]

    num_orders = len(succ_idx)

    order_users = (
        session_users
        .iloc[succ_idx]
        .reset_index(drop=True)
    )

    city_rest_map = (
        restaurants_df
        .groupby('city')['restaurant_id']
        .apply(list)
        .to_dict()
    )

    assigned_rests = [
        np.random.choice(
            city_rest_map.get(
                city,
                restaurants_df['restaurant_id'].tolist()
            )
        )
        for city in order_users['city']
    ]

    order_values = np.clip(
        np.random.lognormal(
            mean=3.0,
            sigma=0.5,
            size=num_orders
        ),
        10,
        200
    ).round(2)

    orders_df = pd.DataFrame({

        'order_id': [
            str(uuid.uuid4())
            for _ in range(num_orders)
        ],

        'user_id':
            order_users['user_id'].values,

        'restaurant_id':
            assigned_rests,

        'session_id':
            sessions_df['session_id'].values[succ_idx],

        'order_timestamp':
            sessions_df['session_start'].values[succ_idx]
            + pd.to_timedelta(
                250,
                unit='s'
            ),

        'order_value':
            order_values,

        'discount_applied':
            np.random.choice(
                [0, 5, 10],
                size=num_orders,
                p=[0.7, 0.2, 0.1]
            ),

        'delivery_fee':
            np.random.choice(
                [0.0, 2.99, 4.99],
                size=num_orders,
                p=[0.4, 0.4, 0.2]
            ),

        'status':
            'completed',

        'cancellation_reason':
            None
    })

    # 5% cancellation rate
    cancel_mask = (
        np.random.rand(num_orders)
        < 0.05
    )

    orders_df.loc[
        cancel_mask,
        'status'
    ] = 'cancelled'

    orders_df.loc[
        cancel_mask,
        'cancellation_reason'
    ] = np.random.choice(
        [
            'customer_request',
            'restaurant_busy',
            'no_couriers'
        ],
        size=cancel_mask.sum()
    )

    orders_df.to_csv(
        os.path.join(DATA_DIR, 'orders.csv'),
        index=False
    )

    print(
        f"Generated {len(orders_df)} orders."
    )

    return (
        sessions_df,
        events_df,
        orders_df
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("Starting data generation...")

    u_df = generate_users()

    r_df = generate_restaurants()

    generate_sessions_and_events(
        u_df,
        r_df
    )

    print("Data generation complete.")
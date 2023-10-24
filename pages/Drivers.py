import duckdb
import streamlit as st
import load.calculate_table


def show_table():

    sql = "select max(round) as round from round_player_standing"

    latest_round = duckdb.sql(sql).df().loc[0]['round']

    st.header(f"Driver results")

    sql = "select driver from driver order by driver"

    selected_drivers = st.multiselect("Select drivers:", default = "PER", options = duckdb.sql(sql).df())

    sql = "select distinct round from result order by round desc"

    selected_rounds = st.multiselect("Select rounds:", default = latest_round, options = duckdb.sql(sql).df())

    driver_filter = f"""and s.driver in ({','.join([f"'{d}'" for d in selected_drivers])})""" if len(selected_drivers) > 0 else ""
    round_filter = f"""and s.round in ({','.join([f"'{r}'" for r in selected_rounds])})""" if len(selected_rounds) > 0 else ""

    sql = f"""
        select
            s.round,
            s.driver,
            s.points_this_round,
            s.points,
            m.multiplier
            --round(s.points_this_round * m.multiplier) as multiplier_points
        from standing s
        join multiplier m on m.driver = s.driver
            and m.round = s.round
        --where s.round = (select max(round) from round_player_standing)
        where 1=1
            {driver_filter}
            {round_filter}
        order by s.round, s.driver
    """
    
    st.dataframe(duckdb.sql(sql).df())



if __name__ == "__main__":
    load.calculate_table.main()
    show_table()

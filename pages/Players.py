import duckdb
import streamlit as st
import load.calculate_table


def show_table():

    sql = "select max(round) as round from round_player_standing"

    latest_round = duckdb.sql(sql).df().loc[0]['round']

    st.header(f"Player stakes")

    sql = "select distinct player from stake order by player"

    selected_players = st.multiselect("Select players:", options = duckdb.sql(sql).df())

    sql = "select distinct round from result order by round desc"

    selected_rounds = st.multiselect("Select rounds:", default = latest_round, options = duckdb.sql(sql).df())

    player_filter = f"""and s.player in ({','.join([f"'{d}'" for d in selected_players])})""" if len(selected_players) > 0 else ""
    round_filter = ""
    if len(selected_rounds) > 0:
        round_filter = 'and (' + ' or '.join([f"{r} between start_round and end_round" for r in selected_rounds]) + ')'

    sql = f"""
        select
            s.start_round,
            s.end_round,
            s.player,
            s.driver,
            s.stake
        from stake s
        where 1=1
            {player_filter}
            {round_filter}
        order by s.start_round, s.end_round, s.player, s.stake
        
    """
    
    st.dataframe(duckdb.sql(sql).df())



if __name__ == "__main__":
    load.calculate_table.main()
    show_table()

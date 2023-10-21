import duckdb
import streamlit as st
import load.calculate_table


def show_table():

    sql = "select max(round) as round from round_player_standing"

    st.header(f"Player stakes - round {duckdb.sql(sql).df().loc[0]['round']}")

    sql = """
        select
            s.player,
            s.driver,
            s.stake
        from stake s
        where end_round = 22
        
    """
    
    st.dataframe(duckdb.sql(sql).df(), height = 800)



if __name__ == "__main__":
    load.calculate_table.main()
    show_table()

import duckdb
import streamlit as st
import load.calculate_table


def show_table():

    sql = "select max(round) as round from round_player_standing"

    st.header(f"Round {duckdb.sql(sql).df().loc[0]['round']}")

    sql = """
        select
            s.driver,
            s.points_this_round,
            s.points,
            m.multiplier
            --round(s.points_this_round * m.multiplier) as multiplier_points
        from standing s
        join multiplier m on m.driver = s.driver
            and m.round = s.round
        where s.round = (select max(round) from round_player_standing)
        order by 3 desc, 2, 1
    """
    
    st.dataframe(duckdb.sql(sql).df(), height = 800)



if __name__ == "__main__":
    load.calculate_table.main()
    show_table()

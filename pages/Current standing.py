import duckdb
import streamlit as st
import load.calculate_table


def show_table():
    sql = """
        select *
        from round_player_standing
        --where player = 'James'
        where round = (select max(round) from round_player_standing)
        order by player_points_total desc
    """
    st.dataframe(duckdb.sql(sql).df())

    sql = """
        with t as (
            select
                round,
                player,
                player_points_total
            from round_player_standing
            where round >= 14
            order by 1, 2, 3
        )
        PIVOT t ON player USING SUM(player_points_total);
    """

    st.line_chart(duckdb.sql(sql).df(), x = "round")



if __name__ == "__main__":
    load.calculate_table.main()
    st.header("Current standing")
    show_table()

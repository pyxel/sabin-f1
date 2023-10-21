import duckdb
import streamlit as st
import load.calculate_table


def show_table():
    sql = """
        select *
        from round_player_standing
        --where player = 'James'
        where round = 18
        order by player_points_total desc
    """
    sql = """
        select
            round,
            player,
            driver,
            points_this_round as driver_points_this_round,
            multiplier,
            stake,
            player_points_this_round
        from player_standing
        where round = 18
        order by 1,2,3
    """
    sql = """
        select
            driver,
            round,
            multiplier
        from multiplier
        where driver = 'LAW'
            and round >= 1
        order by 1,2,3
    """
    sql = """
        select
            s.driver,
            s.round,
            s.points_this_round,
            round(s.points_this_round * m.multiplier) as multiplier_points
        from standing s
        join multiplier m on m.driver = s.driver
            and m.round = 
        where s.round = (select max(round) from round_player_standing)
        order by 3 desc, 2, 1
    """
    sql = """
        select
            s.driver,
            m.multiplier,
            sum(round(s.points_this_round * m.multiplier)) as multiplier_points
        from standing s
        join multiplier m on m.driver = s.driver
            and m.round = 14
        where s.round >= 14
        group by all
        order by 3 desc, 2 desc, 1
    """
    sql2 = """
        select
            round,
            player,
            player_points_this_round
        from round_player_standing
        order by 3 desc, 1, 2
        limit 15
    """
    #duckdb.sql(sql).show()
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
    #duckdb.sql(sql).show()
    st.line_chart(duckdb.sql(sql).df(), x = "round")
    st.area_chart(duckdb.sql(sql).df(), x = "round")


if __name__ == "__main__":
    load.calculate_table.main()
    show_table()

import duckdb
import streamlit as st
import load.calculate_table


def show_table():

    st.header(f"Drivers: Most points by round")
    st.write(f"Multipliers shown are the multipliers for the driver on that round. More points could be scored if the driver was already contracted at a higher multiplier.")

    sql = """
        with ps as (
            select
                rd.round,
                s.driver,
                string_agg(s.player||' ('||s.stake||')', ' | ') as players
            from (select distinct round from standing where round >= 14) as rd
            join stake s on rd.round between s.start_round and s.end_round
            group by all
        )

        select
            s.round,
            s.driver,
            s.points_this_round,
            m.multiplier,
            round(s.points_this_round * m.multiplier) as multiplier_points,
            ps.players as "player (stake)"
        from standing s
        join multiplier m on m.driver = s.driver
            and m.round = s.round
        left join ps on ps.round = s.round
            and ps.driver = s.driver
        where s.round >= 14
        qualify row_number() over(partition by s.round order by multiplier_points desc) <= 3
        order by s.round, multiplier_points desc
    """
    
    st.dataframe(duckdb.sql(sql).df(), height = 800, width = 700)



if __name__ == "__main__":
    load.calculate_table.main()
    show_table()

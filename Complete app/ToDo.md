1. Přidat jednotný způsob pro resetování solveru se zachováním současných hodnot grafu.
    - Algoritmus pro přidání elementu:
        1. vytvořit element ve VariableChart
        1. resetovat solver
        1. nahrát do solveru constrainty z VariableChart a edit variables (initial hodnoty musí odpovídat aktuálním hodnotám)
    - při nejhorším prostě všechno vyhodit a dát tam nový
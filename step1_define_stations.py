neighbors = {
    "Zurich": ["Aargau", "Zug", "Schwyz", "St. Gallen", "Thurgau", "Schaffhausen", "Basel-Stadt"],
    "St. Gallen": ["Thurgau", "Zurich", "Schwyz", "Glarus", "Graubünden", "Appenzell Ausserrhoden", "Appenzell Innerrhoden"],
    "Appenzell Ausserrhoden": ["St. Gallen", "Appenzell Innerrhoden"],
    "Appenzell Innerrhoden": ["St. Gallen", "Appenzell Ausserrhoden"],
    "Thurgau": ["St. Gallen", "Zurich", "Schaffhausen"],
    "Schaffhausen": ["Zurich", "Thurgau"],
    "Glarus": ["St. Gallen", "Schwyz", "Uri", "Graubünden"],
    "Lucerne": ["Aargau", "Zug", "Schwyz", "Nidwalden", "Obwalden", "Bern"],
    "Zug": ["Zurich", "Aargau", "Lucerne", "Schwyz"],
    "Schwyz": ["Zurich", "Zug", "Lucerne", "Nidwalden", "Uri", "Glarus", "St. Gallen"],
    "Uri": ["Schwyz", "Glarus", "Graubünden", "Ticino", "Valais", "Bern", "Obwalden", "Nidwalden"],
    "Nidwalden": ["Lucerne", "Obwalden", "Uri", "Schwyz", "Bern"],
    "Obwalden": ["Lucerne", "Nidwalden", "Uri", "Bern"],
    "Basel-Stadt": ["Basel-Landschaft", "Aargau", "Solothurn", "Zurich"],
    "Basel-Landschaft": ["Basel-Stadt", "Aargau", "Solothurn", "Jura"],
    "Aargau": ["Basel-Landschaft", "Solothurn", "Bern", "Lucerne", "Zug", "Zurich", "Basel-Stadt"],
    "Solothurn": ["Basel-Landschaft", "Jura", "Bern", "Aargau", "Basel-Stadt"],
    "Jura": ["Basel-Landschaft", "Solothurn", "Bern", "Neuchâtel"],
    "Bern": ["Jura", "Solothurn", "Aargau", "Lucerne", "Obwalden", "Nidwalden", "Uri", "Valais", "Fribourg", "Vaud", "Neuchâtel"],
    "Fribourg": ["Bern", "Vaud", "Neuchâtel"],
    "Neuchâtel": ["Jura", "Bern", "Fribourg", "Vaud"],
    "Geneva": ["Vaud"],
    "Vaud": ["Geneva", "Valais", "Bern", "Fribourg", "Neuchâtel"],
    "Valais": ["Vaud", "Bern", "Uri", "Ticino"],
    "Ticino": ["Graubünden", "Uri", "Valais"],
    "Graubünden": ["St. Gallen", "Glarus", "Uri", "Ticino"]
}

swiss_canton_stations_old = {
    # German-speaking cantons
    "Aargau": ["Aarau", "Zofingen", "Sins", "Brugg AG", "Aarburg, Kloosmatte"],
    "Appenzell Ausserrhoden": ["Herisau", "Gais", "Urnäsch"],
    "Appenzell Innerrhoden": ["Appenzell", "Jakobsbad", "Sammelplatz"],
    "Basel-Landschaft": ["Liestal", "Laufen", "Muttenz"],
    "Basel-Stadt": ["Basel SBB"],
    "Bern": ["Bern", "Biel/Bienne"],
    "Glarus": ["Glarus", "Ziegelbrücke", "Mühlehorn", "Bilten"],
    "Graubünden": ["Chur", "Thusis", "Landquart", "Disentis", "S. Vittore, Zona industriale"],
    "Lucerne": ["Luzern", "Sursee"],
    "Nidwalden": ["Stans", "Hergiswil NW", "Stansstad"],
    "Obwalden": ["Sarnen", "Alpnachstad"],
    "Schaffhausen": ["Schaffhausen", "Neuhausen"],
    "Schwyz": ["Schwyz", "Arth-Goldau" , "Pfäffikon SZ"],
    "Solothurn": ["Solothurn", "Olten", "Grenchen Nord"],
    "St. Gallen": ["St. Gallen", "Rapperswil", "Wattwil", "Wil SG", "Sargans", "Uznach"],
    "Thurgau": ["Frauenfeld", "Romanshorn", "Münchwilen TG"],
    "Uri": ["Altdorf", "Erstfeld", "Göschenen"],
    "Zug": ["Zug"],
    "Zurich": ["Zürich HB", "Langwiesen ZH"],
    
    # French-speaking cantons
    "Fribourg": ["Fribourg", "Estavayer-le-Lac", "Kerzers", "Romont FR"],
    "Geneva": ["Genève", "Pont-Céard"],
    "Jura": ["Delémont"],
    "Neuchâtel": ["Neuchâtel", "Marin-Epagnier", "Le Landeron"],
    "Vaud": ["Lausanne", "Renens VD", "Palézieux"],
    "Valais": ["Sion", "Martigny", "St-Maurice", "Brig", "Gletsch"],
    
    # Italian-speaking canton
    "Ticino": ["Bellinzona", "Biasca", "Airolo", "Castione-Arbedo"]
}

swiss_canton_stations = {
    # German-speaking cantons
    "Aargau": ["Aarau", "Zofingen", "Baden", "Brugg AG", "Aarburg, Kloosmatte"],
    "Appenzell Ausserrhoden": ["Herisau", "Heiden, Post"],
    "Appenzell Innerrhoden": ["Jakobsbad", "Oberegg, Post"],
    "Basel-Landschaft": ["Liestal", "Muttenz", "Laufen, Bahnhof"],
    "Basel-Stadt": ["Basel SBB"],
    "Bern": ["Bern", "Biel/Bienne", "Lyss"],
    "Glarus": ["Ziegelbrücke", "Mühlehorn"],
    "Graubünden": ["Landquart", "S. Vittore, Zona industriale"],
    "Lucerne": ["Luzern", "Sursee"],
    "Nidwalden": ["Hergiswil NW"],
    "Obwalden": ["Alpnachstad"],
    "Schaffhausen": ["Schaffhausen", "Neuhausen", "Stein am Rhein"],
    "Schwyz": ["Arth-Goldau", "Pfäffikon SZ"],
    "Solothurn": ["Olten", "Grenchen Nord"],
    "St. Gallen": ["St. Gallen", "Rapperswil", "Wattwil", "Wil SG", "Sargans", "Uznach", "Gossau SG", "Heerbrugg", "Rheineck", "St. Gallen St. Fiden"],
    "Thurgau": ["Frauenfeld", "Romanshorn", "Aadorf", "Sirnach", "Münchwilen TG"],
    "Uri": ["Altdorf UR"],
    "Zug": ["Zug"],
    "Zurich": ["Zürich HB", "Langwiesen ZH"],
    
    # French-speaking cantons
    "Fribourg": ["Fribourg", "Kerzers"],
    "Geneva": ["Genève"],
    "Jura": ["Delémont"],
    "Neuchâtel": ["Neuchâtel", "Le Landeron"],
    "Vaud": ["Lausanne", "Renens VD"],
    "Valais": ["St-Maurice"],
    
    # Italian-speaking canton
    "Ticino": ["Bellinzona", "Biasca", "Castione-Arbedo"]
}
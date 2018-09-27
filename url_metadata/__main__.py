from . import app, table_check

# This code checks whether database table is created or not
table_check()
# app.run(debug=True)
app.run(host='0.0.0.0')

## Purpose
Creating custom analytics and visualizations based on activty data exported from Strava. Strava allows for the export of GPX files, which contain the tracking data for individual activities. By analyzing this using Python, we can create custom insights not found through Strava's interface.

There are multiple Jupyter Notebooks that perfrom different analyses. <br>
There is also a web app located at https://kempton.pythonanywhere.com

For example, one maps previous rides:
<img src="https://github.com/fkmooney/Non-Work-Analyses/Strava/map.png" width="600" >

## Things to do


### For aggregated feeds

improvement over time for same rides:
 - avg speed <br>
 - zone analysis <br>
 - distance vs date scatter plot with size for elevation gain<br>
 - relative effort, [more info here](https://https://medium.com/strava-engineering/quantifying-effort-through-heart-rate-data-e6a0e3dd6a52#id_token=eyJhbGciOiJSUzI1NiIsImtpZCI6ImVlMWI5Zjg4Y2ZlMzE1MWRkZDI4NGE2MWJmOGNlY2Y2NTliMTMwY2YiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJuYmYiOjE2NjY0NzU0NTcsImF1ZCI6IjIxNjI5NjAzNTgzNC1rMWs2cWUwNjBzMnRwMmEyamFtNGxqZGNtczAwc3R0Zy5hcHBzLmdvb2dsZXVzZXJjb250ZW50LmNvbSIsInN1YiI6IjExNTI3MDU1ODQ2NjM2NTkxMzQ0NCIsImVtYWlsIjoia2VtcHRvbi5tb29uZXlAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImF6cCI6IjIxNjI5NjAzNTgzNC1rMWs2cWUwNjBzMnRwMmEyamFtNGxqZGNtczAwc3R0Zy5hcHBzLmdvb2dsZXVzZXJjb250ZW50LmNvbSIsIm5hbWUiOiJLZW1wdG9uIE1vb25leSIsInBpY3R1cmUiOiJodHRwczovL2xoMy5nb29nbGV1c2VyY29udGVudC5jb20vYS9BTG01d3UxLV82dV9ub19iVmVKVHlicXpwaFIxdU9ERElvZm1UdnFESVJ2MT1zOTYtYyIsImdpdmVuX25hbWUiOiJLZW1wdG9uIiwiZmFtaWx5X25hbWUiOiJNb29uZXkiLCJpYXQiOjE2NjY0NzU3NTcsImV4cCI6MTY2NjQ3OTM1NywianRpIjoiNjllMDNkNzJlNDRjNDk3NTk2ZmM5YmFlZmM2ZTQ0MGU0YjZlOGE5YyJ9.mStzcnHAiHrX8Ld3EoHqg3CMsIWlyjHp-ymzxK8eOQvKDV40IqfroaiyiCjGIOAGKBcQ_HDFUXO-MW_gvSjg9GjfLawXU9Nt7MnzprDTOe4OH3b3AP4a5PCqjaY9liX6euLq-EOQtjmSgVdG3VnDP2bBDrmAt4ZQvbnW-Xj2bvd88EEKotxGyyQVSheaorMS8t90z06ABOylFsxtHKG-mnxqp0eyT-sRDLO95jIYh-PPHtk1zoGWL2Fn93N1S7UuVfSg6i7KarpTzQLNJT8Z0cCe36N9XKP8TygiBjHwc8OsEgrEYHRSEqDh7UwVkkDozwlzyrxyUqq5wQtrPVfrmg)<br>
 
### Inspiration:
https://veloviewer.com/<br>

https://marcusvolz.com/strava/<br>
 - A GitHub style calendar showing daily distance in kilometres.<br>
 - Each run is a circle. Run distance is mapped to circle area. speed is color<br>
 - annual retrospective<br>
 - maxes and totals for year<br>

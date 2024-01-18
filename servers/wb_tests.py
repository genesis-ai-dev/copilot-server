import sys
import wildebeest.wb_analysis as wb_ana

wb = wb_ana.process(string="Helo Hello hello hllo 𝗛ᴇᴌʟo", json_output=open("test2.json", "w+")) # "Hеllο!" mischievously includes a Cyrillic and a Greek character

wb.pretty_print(sys.stdout)


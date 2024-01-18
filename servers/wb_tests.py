import sys
import wildebeest.wb_analysis as analyze

wb = analyze.process(string = "मेरे dear friend, let's haमेरेe a cup of chai in the garden and discuss the philosophia of life").summary_list_of_issues()
print(wb)
# wb.pretty_print(sys.stdout)

#wb = wb_ana.process(string="Helo Hello hello hllo 𝗛ᴇᴌʟo", json_output=open("test2.json", "w+")) # "Hеllο!" mischievously includes a Cyrillic and a Greek character

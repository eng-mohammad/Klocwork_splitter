import re
import wx
from os.path import dirname
# from bs4 import BeautifulSoup

class klocworksplitGui(wx.Frame):
    def __init__(self, parent, id):
        #global variables
        self.Severity = ""

        #wx script
        wx.Frame.__init__(self, parent, id, 'KlocWork report split', size=(600, 250))
        self.panel = wx.Panel(self)
        self.Bind(wx.EVT_CLOSE, self.closewindow)

        #file picker
        self.FileBrowse = wx.FilePickerCtrl(self.panel, message='Select Klocwork Report', style=wx.FLP_OPEN, pos=(400, 20))

        # Buttons
        self.GenerateBuuton = wx.Button(self.panel, label='Generate Component report', pos=(380, 150), size=(180, 40))
        
        #Text Boxes
        self.reportPath = wx.TextCtrl(self.panel, size=(350, -1), pos=(20, 20))
        self.SearchFile = wx.TextCtrl(self.panel, size=(200, -1), pos=(100, 50))
        self.SearchStatus = wx.TextCtrl(self.panel, size=(200, -1), pos=(100, 110))

        #Labels
        self.File = wx.StaticText(self.panel, label='File', pos=(20, 53))
        self.Severity = wx.StaticText(self.panel, label='Severity', pos=(20, 83))
        self.Status = wx.StaticText(self.panel, label='Status', pos=(20, 113))

        #Check Boxes
        self.all = wx.CheckBox(self.panel, label='ALL', pos=(100, 83))
        self.critical = wx.CheckBox(self.panel, label='Critical', pos=(200, 83))
        self.error = wx.CheckBox(self.panel, label='Error', pos=(300, 83))
        self.warning = wx.CheckBox(self.panel, label='Warning', pos=(400, 83))
        self.review = wx.CheckBox(self.panel, label='Review', pos=(500, 83))

        #event binding
        self.Bind(wx.EVT_BUTTON, self.generatereport, self.GenerateBuuton)
        self.Bind(wx.EVT_CHECKBOX, self.allcheck, self.all)
        self.Bind(wx.EVT_CHECKBOX, self.severitycheck, self.critical)
        self.Bind(wx.EVT_CHECKBOX, self.severitycheck, self.error)
        self.Bind(wx.EVT_CHECKBOX, self.severitycheck, self.warning)
        self.Bind(wx.EVT_CHECKBOX, self.severitycheck, self.review)
        self.Bind(wx.EVT_FILEPICKER_CHANGED, self.filepathgetter, self.FileBrowse)

        #update severity
        self.severitycheck(0)


    def filepathgetter(self, event):
        self.reportPath.SetValue(self.FileBrowse.GetPath())


    def generatereport(self, event):
        sw_component = str(self.SearchFile.GetValue())
        
        #pattern = re.compile('\{"id".*""severity":"' + self.Severity + '".*Source.*' + sw_component + '.*"issueIds".*\}', re.IGNORECASE)
        regex_text = '\{"id".*"severity":' + self.Severity.__str__() + '.*Source.*' + sw_component + '.*","method":.*"issueIds".*\}'
        pattern = re.compile(regex_text, re.IGNORECASE)
        
        with open('report_template/klocwork_report.html', 'r') as f:
            html_data = f.readlines()

        with open(self.FileBrowse.GetPath(), 'r') as f:
            contents = f.read()
            matches = pattern.finditer(contents)

        html_data[46] = re.search('<h2>.*<\/h2>', contents).group(0)
        html_data[47] = re.search('<h3>.*<\/h3>', contents).group(0)

        defect_log = []

        #Progress Dialog
        self.progressDialog = wx.ProgressDialog('klocwork split', 'klocwork split ...', maximum=100, style=wx.PD_SMOOTH)

        for match in matches:
            self.progressDialog.Pulse()
            defect_log.append(str(match.group(0)))

        report_text = ''
        for defect in defect_log:
            report_text += defect
            report_text += ',\n'

        report_text = report_text[:-2] + '\n'

        html_data[15] = report_text

        with open(dirname(self.FileBrowse.GetPath()) + '\\' + sw_component + '_report.html', 'w') as f:
            f.writelines(html_data)

        self.progressDialog.Destroy()
        okMSG = wx.MessageDialog(self, message=sw_component + ' report has been generated', style=wx.OK|wx.CENTRE, pos=wx.DefaultPosition)
        okMSG.ShowModal()


    def severitycheck(self, event):
        self.Severity = ""
        if self.critical.IsChecked():
            if self.Severity == '':
                self.Severity = '"('
            self.Severity += 'Critical'

        if self.error.IsChecked():
            if self.Severity == '':
                self.Severity = '"('
                self.Severity += 'Error'
            else:
                self.Severity += '|Error'

        if self.warning.IsChecked():
            if self.Severity == '':
                self.Severity = '"('
                self.Severity += 'Warning'
            else:
                self.Severity += '|Warning'

        if self.review.IsChecked():
            if self.Severity == '':
                self.Severity = '"('
                self.Severity += 'Review'
            else:
                self.Severity += '|Review'

        if self.Severity != '':
                self.Severity += ')"'

        if not self.critical.IsChecked() or not self.error.IsChecked() or not self.warning.IsChecked() or not self.review.IsChecked():
            self.all.SetValue(False)
        else:
            self.all.SetValue(True)


    def allcheck(self, event):
        if self.all.IsChecked():
            self.critical.SetValue(True)
            self.error.SetValue(True)
            self.warning.SetValue(True)
            self.review.SetValue(True)
        else:
            self.critical.SetValue(False)
            self.error.SetValue(False)
            self.warning.SetValue(False)
            self.review.SetValue(False)
        self.severitycheck(event)


    def closewindow(self, event):
        self.Destroy()

if __name__ == '__main__':
    app = wx.PySimpleApp()
    app.MainLoop()
    frame = klocworksplitGui(parent=None, id=-1)
    frame.Show()
    app.MainLoop()
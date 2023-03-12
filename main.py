import os.path
import chromedriver_autoinstaller
import wx
from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException, NoSuchWindowException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service as ChromeService
from subprocess import CREATE_NO_WINDOW
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

chromedriver_autoinstaller.install()
usernameFilename = 'config.ini'
passwordFilename = 'setup.ini'

if not os.path.isfile(usernameFilename):
    file = open(usernameFilename, 'w+')
    file.close()

if not os.path.isfile(passwordFilename):
    file = open(passwordFilename, 'w+')
    file.close()


class MainFrame(wx.Frame):

    def __init__(self, *args, **kw):
        # ensure the parent's __init__ is called
        super(MainFrame, self).__init__(*args, **kw)
        self.Driver = None
        width = 325
        height = 400
        self.SetSize(wx.Size(width, height))
        self.SetIcon(wx.Icon('icon.png'))
        self.SetBackgroundColour(wx.Colour(150, 150, 150))

        # create a panel in the frame
        pnl = wx.Panel(self)

        # put some text with a larger bold font on it
        st = wx.StaticText(pnl, label="Chess2Board")
        font = st.GetFont()
        font.PointSize += 10
        font = font.Bold()
        st.SetFont(font)

        # Login and Password text fields
        usernameFile = open(usernameFilename, 'r+')
        self.username = usernameFile.readline().strip('\n')
        usernameFile.close()
        loginTitle = wx.StaticText(pnl, label='Chess.com Login:         ')
        loginCtrl = wx.TextCtrl(pnl, value=self.username)
        loginCtrl.Bind(wx.EVT_TEXT, self.OnChangeUsername)
        loginCtrl.Bind(wx.EVT_ENTER_WINDOW, self.OnHoverCredentials)
        loginCtrl.Bind(wx.EVT_LEAVE_WINDOW, self.OnStopHoverCredentials)

        passwordFile = open(passwordFilename, 'r+')
        self.password = passwordFile.readline().strip('\n')
        passwordTitle = wx.StaticText(pnl, label='Chess.com Password:  ')
        passwordCtrl = wx.TextCtrl(pnl, value=self.password, style=wx.TE_PASSWORD)
        passwordCtrl.Bind(wx.EVT_TEXT, self.OnChangePassword)
        passwordCtrl.Bind(wx.EVT_ENTER_WINDOW, self.OnHoverCredentials)
        passwordCtrl.Bind(wx.EVT_LEAVE_WINDOW, self.OnStopHoverCredentials)

        # Create chess.com/analysis button
        AnalysisBtn = wx.Button(pnl, label="Chess.com/analysis")
        AnalysisBtn.Bind(wx.EVT_BUTTON, self.OnClickAnalysis)
        AnalysisBtn.Bind(wx.EVT_ENTER_WINDOW, self.OnHoverAnalysis)
        AnalysisBtn.Bind(wx.EVT_LEAVE_WINDOW, self.OnStopHoverAnalysis)

        # Create chess.com/play/computer button
        CompBtn = wx.Button(pnl, label="Chess.com/computer")
        CompBtn.Bind(wx.EVT_BUTTON, self.OnClickComp)
        CompBtn.Bind(wx.EVT_ENTER_WINDOW, self.OnHoverComp)
        CompBtn.Bind(wx.EVT_LEAVE_WINDOW, self.OnStopHoverComp)

        # Create TextCtrl for handling move input
        MoveTitle = wx.StaticText(pnl, label='Move in UCI:   ')
        self.MoveInput = wx.TextCtrl(pnl, style=wx.TE_PROCESS_ENTER)
        self.MoveInput.Bind(wx.EVT_TEXT_ENTER, self.OnInputMove)
        self.MoveInput.Bind(wx.EVT_ENTER_WINDOW, self.OnHoverMove)
        self.MoveInput.Bind(wx.EVT_LEAVE_WINDOW, self.OnStopHoverMove)

        # Create a sizer to manage the layout of child widgets
        MainText = wx.BoxSizer(wx.VERTICAL)
        MainText.Add(st, wx.SizerFlags().Border(wx.TOP, 20))

        LoginHolder = wx.BoxSizer(wx.HORIZONTAL)
        LoginHolder.Add(loginTitle, 0, wx.CENTER)
        LoginHolder.Add(loginCtrl, 0, wx.CENTER)

        PasswordHolder = wx.BoxSizer(wx.HORIZONTAL)
        PasswordHolder.Add(passwordTitle, 0, wx.CENTER)
        PasswordHolder.Add(passwordCtrl, 0, wx.CENTER)

        CredentialsHolder = wx.BoxSizer(wx.VERTICAL)
        CredentialsHolder.Add(LoginHolder, wx.SizerFlags().Border(wx.TOP, 25))
        CredentialsHolder.Add(PasswordHolder, wx.SizerFlags().Border(wx.TOP, 10))

        ButtonHolder = wx.BoxSizer(wx.HORIZONTAL)
        ButtonHolder.Add(AnalysisBtn, wx.SizerFlags().Border(wx.TOP, 25))
        ButtonHolder.Add(CompBtn, wx.SizerFlags().Border(wx.TOP | wx.LEFT, 25))

        MoveHolder = wx.BoxSizer(wx.HORIZONTAL)
        MoveYHolder = wx.BoxSizer(wx.VERTICAL)
        MoveHolder.Add(MoveTitle, 0, wx.CENTER)
        MoveHolder.Add(self.MoveInput, 0, wx.CENTER)
        MoveYHolder.Add(MoveHolder, wx.SizerFlags().Border(wx.TOP, 25))

        ysizer = wx.BoxSizer(wx.VERTICAL)
        ysizer.Add(MainText, 0, wx.CENTER)
        ysizer.Add(CredentialsHolder, 0, wx.CENTER)
        ysizer.Add(ButtonHolder, 0, wx.CENTER)
        ysizer.Add(MoveYHolder, 0, wx.CENTER)

        pnl.SetSizer(ysizer)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Create status bar
        self.defaultStatusText = "Welcome to Chess2Board!"
        self.CreateStatusBar()
        self.SetStatusText(self.defaultStatusText)

    def OnInputMove(self, event):
        move = event.GetString()
        if len(move) != 4:
            wx.MessageBox("That is not a valid move!")
            return
        if self.Driver is None:
            wx.MessageBox("No window open to click on!")
            return
        fromX = slice(0, 1)
        fromx = ord(move[fromX]) - 96
        fromY = slice(1, 2)
        fromy = move[fromY]
        toX = slice(2, 3)
        tox = ord(move[toX]) - 96
        toY = slice(3, 4)
        toy = move[toY]
        try:
            click_square(int(fromx) * 99 - 443, int(fromy) * -99 + 443,
                         int(tox) * 99 - 443, int(toy) * -99 + 443, self.Driver)
        except NoSuchWindowException:
            wx.MessageBox("No window open to click on!")
        self.MoveInput.SetValue('')

    def OnHoverMove(self, event):
        self.StatusBar.SetStatusText("Input your move in UCI (e2e4, b1c3, etc.)")

    def OnStopHoverMove(self, event):
        self.StatusBar.SetStatusText(self.defaultStatusText)

    def OnChangeUsername(self, event):
        self.username = event.GetString()
        configFile = open(usernameFilename, 'w')
        configFile.write(event.GetString())
        configFile.close()

    def OnChangePassword(self, event):
        self.password = event.GetString()
        configFile = open(passwordFilename, 'w')
        configFile.write(event.GetString())
        configFile.close()

    def OnHoverCredentials(self, event):
        self.StatusBar.SetStatusText('Input your Chess.com credentials')

    def OnStopHoverCredentials(self, event):
        self.StatusBar.SetStatusText("Welcome to Chess2Board!")

    def OnHoverComp(self, event):
        self.StatusBar.SetStatusText("Launch Chess.com to play against computers")

    def OnStopHoverComp(self, event):
        self.StatusBar.SetStatusText(self.defaultStatusText)

    def OnClickComp(self, event):
        if self.username == '' or self.password == '':
            self.Driver = openChessComp(self.username, self.password, True)
        else:
            self.Driver = openChessComp(self.username, self.password, False)

    def OnHoverAnalysis(self, event):
        self.StatusBar.SetStatusText("Launch Chess.com to analyze moves")

    def OnStopHoverAnalysis(self, event):
        self.StatusBar.SetStatusText(self.defaultStatusText)

    def OnClickAnalysis(self, event):
        if self.username == '' or self.password == '':
            self.Driver = openChessAnalysis(self.username, self.password, True)
        else:
            self.Driver = openChessAnalysis(self.username, self.password, False)

    def OnClose(self, event):
        if self.Driver is not None:
            self.Driver.quit()
        self.Destroy()


def openChessComp(username, password, Guest):
    chrome_service = ChromeService('chromedriver')
    chrome_service.creationflags = CREATE_NO_WINDOW
    prefs = {"credentials_enable_service": False,
             "profile.password_manager_enabled": False}
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_experimental_option("prefs", prefs)
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    Driver = webdriver.Chrome(service=chrome_service, options=options)
    if not Guest:
        Driver.get("https://www.chess.com/login_and_go?returnUrl=https%3A//www.chess.com/play/computer")
        login = Driver.find_element(By.ID, "username")
        login.click()
        login.send_keys(username)
        login2 = Driver.find_element(By.ID, "password")
        login2.click()
        login2.send_keys(password)
        button = Driver.find_element(By.ID, "login")
        button.click()
    else:
        Driver.get("https://www.chess.com/play/computer")
    try:
        Button = WebDriverWait(Driver, 10).until(ec.element_to_be_clickable((By.XPATH, '//button[text()="Start"]')))
        Button.click()
    except TimeoutException:
        print("")

    return Driver


def openChessAnalysis(username, password, Guest):
    chrome_service = ChromeService('chromedriver')
    chrome_service.creationflags = CREATE_NO_WINDOW
    prefs = {"credentials_enable_service": False,
             "profile.password_manager_enabled": False}
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_experimental_option("prefs", prefs)
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    Driver = webdriver.Chrome(service=chrome_service, options=options)
    if not Guest:
        Driver.get("https://www.chess.com/login_and_go?returnUrl=https%3A//www.chess.com/analysis")
        login = Driver.find_element(By.ID, "username")
        login.click()
        login.send_keys(username)
        login2 = Driver.find_element(By.ID, "password")
        login2.click()
        login2.send_keys(password)
        button = Driver.find_element(By.ID, "login")
        button.click()
    else:
        Driver.get("https://www.chess.com/analysis")
    return Driver


def click_square(fromCol, fromRow, toCol, toRow, Driver):
    try:
        elem = Driver.find_element(By.CLASS_NAME, 'flipped')
        fromCol = fromCol * -1
        fromRow = fromRow * -1
        toCol = toCol * -1
        toRow = toRow * -1

    except NoSuchElementException:
        elem = Driver.find_element(By.CLASS_NAME, 'board')

    action_chains = ActionChains(Driver)
    action_chains.move_to_element_with_offset(elem, fromCol, fromRow).click().perform()
    action_chains.move_to_element_with_offset(elem, toCol, toRow).click().perform()


if __name__ == '__main__':
    app = wx.App()
    frm = MainFrame(None, title='Chess2Board')
    frm.Show()
    app.MainLoop()

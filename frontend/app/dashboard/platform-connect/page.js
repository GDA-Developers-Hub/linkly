"use client";
"use strict";
var __assign = (this && this.__assign) || function () {
    __assign = Object.assign || function(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                t[p] = s[p];
        }
        return t;
    };
    return __assign.apply(this, arguments);
};
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g = Object.create((typeof Iterator === "function" ? Iterator : Object).prototype);
    return g.next = verb(0), g["throw"] = verb(1), g["return"] = verb(2), typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (g && (g = 0, op[0] && (_ = 0)), _) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.default = PlatformConnectPage;
var react_1 = require("react");
var button_1 = require("@/components/ui/button");
var card_1 = require("@/components/ui/card");
var tabs_1 = require("@/components/ui/tabs");
var badge_1 = require("@/components/ui/badge");
var alert_1 = require("@/components/ui/alert");
var switch_1 = require("@/components/ui/switch");
var label_1 = require("@/components/ui/label");
var input_1 = require("@/components/ui/input");
var lucide_react_1 = require("lucide-react");
var dialog_1 = require("@/components/ui/dialog");
var dropdown_menu_1 = require("@/components/ui/dropdown-menu");
var separator_1 = require("@/components/ui/separator");
var mode_toggle_1 = require("@/components/mode-toggle");
var socialbu_api_1 = require("@/lib/socialbu-api");
var use_toast_1 = require("@/components/ui/use-toast");
// Map platform names to icons and colors
var platformConfig = {
    facebook: { icon: lucide_react_1.Facebook, color: "#1877F2" },
    instagram: { icon: lucide_react_1.Instagram, color: "#E1306C" },
    twitter: { icon: lucide_react_1.Twitter, color: "#1DA1F2" },
    linkedin: { icon: lucide_react_1.Linkedin, color: "#0A66C2" },
    youtube: { icon: lucide_react_1.Youtube, color: "#FF0000" },
    tiktok: { icon: lucide_react_1.TwitterIcon, color: "#000000" },
    pinterest: { icon: lucide_react_1.PinIcon, color: "#E60023" },
};
function PlatformConnectPage() {
    var _this = this;
    var _a = (0, react_1.useState)("connected"), activeTab = _a[0], setActiveTab = _a[1];
    var _b = (0, react_1.useState)(false), isRefreshing = _b[0], setIsRefreshing = _b[1];
    var _c = (0, react_1.useState)([]), connectedAccounts = _c[0], setConnectedAccounts = _c[1];
    var _d = (0, react_1.useState)(false), hasError = _d[0], setHasError = _d[1];
    var _e = (0, react_1.useState)(true), hasToken = _e[0], setHasToken = _e[1];
    var _f = (0, react_1.useState)(false), isAuthDialogOpen = _f[0], setIsAuthDialogOpen = _f[1];
    var _g = (0, react_1.useState)("login"), authType = _g[0], setAuthType = _g[1];
    var _h = (0, react_1.useState)({
        name: "",
        email: "",
        password: "",
        retypePassword: "",
    }), authForm = _h[0], setAuthForm = _h[1];
    var toast = (0, use_toast_1.useToast)().toast;
    // Check if user has a token
    var checkUserToken = function () { return __awaiter(_this, void 0, void 0, function () {
        var error_1;
        var _this = this;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    _a.trys.push([0, 2, , 3]);
                    return [4 /*yield*/, (0, socialbu_api_1.withErrorHandling)(function () { return __awaiter(_this, void 0, void 0, function () {
                            var api, hasValidToken;
                            return __generator(this, function (_a) {
                                switch (_a.label) {
                                    case 0:
                                        api = (0, socialbu_api_1.getSocialBuAPI)();
                                        return [4 /*yield*/, api.checkToken()];
                                    case 1:
                                        hasValidToken = _a.sent();
                                        setHasToken(hasValidToken);
                                        if (!hasValidToken) {
                                            setIsAuthDialogOpen(true);
                                            setAuthType("register");
                                        }
                                        return [2 /*return*/];
                                }
                            });
                        }); }, "Failed to verify authentication status")];
                case 1:
                    _a.sent();
                    return [3 /*break*/, 3];
                case 2:
                    error_1 = _a.sent();
                    console.error("Error checking token:", error_1);
                    setHasToken(false);
                    return [3 /*break*/, 3];
                case 3: return [2 /*return*/];
            }
        });
    }); };
    // Handle auth form input changes
    var handleAuthFormChange = function (e) {
        var _a = e.target, name = _a.name, value = _a.value;
        setAuthForm(function (prev) {
            var _a;
            return (__assign(__assign({}, prev), (_a = {}, _a[name] = value, _a)));
        });
    };
    // Handle registration submission
    var handleRegister = function () { return __awaiter(_this, void 0, void 0, function () {
        var api, error_2;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    if (authForm.password !== authForm.retypePassword) {
                        toast({
                            title: "Passwords don't match",
                            description: "Please make sure both passwords match.",
                            variant: "destructive",
                        });
                        return [2 /*return*/];
                    }
                    _a.label = 1;
                case 1:
                    _a.trys.push([1, 3, , 4]);
                    api = (0, socialbu_api_1.getSocialBuAPI)();
                    return [4 /*yield*/, api.register(authForm.name, authForm.email, authForm.password)];
                case 2:
                    _a.sent();
                    toast({
                        title: "Registration successful",
                        description: "Your account has been created. Please log in to continue.",
                    });
                    // Switch to login form
                    setAuthType("login");
                    return [3 /*break*/, 4];
                case 3:
                    error_2 = _a.sent();
                    toast({
                        title: "Registration failed",
                        description: error_2 instanceof Error ? error_2.message : "Failed to register account",
                        variant: "destructive",
                    });
                    return [3 /*break*/, 4];
                case 4: return [2 /*return*/];
            }
        });
    }); };
    // Handle login submission
    var handleLogin = function () { return __awaiter(_this, void 0, void 0, function () {
        var api, error_3;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    _a.trys.push([0, 2, , 3]);
                    api = (0, socialbu_api_1.getSocialBuAPI)();
                    return [4 /*yield*/, api.authenticate(authForm.email, authForm.password)];
                case 1:
                    _a.sent();
                    toast({
                        title: "Login successful",
                        description: "You have been authenticated with SocialBu.",
                    });
                    setHasToken(true);
                    setIsAuthDialogOpen(false);
                    // Refresh accounts after successful login
                    fetchAccounts();
                    return [3 /*break*/, 3];
                case 2:
                    error_3 = _a.sent();
                    toast({
                        title: "Login failed",
                        description: error_3 instanceof Error ? error_3.message : "Failed to authenticate",
                        variant: "destructive",
                    });
                    return [3 /*break*/, 3];
                case 3: return [2 /*return*/];
            }
        });
    }); };
    // Fetch connected accounts
    var fetchAccounts = function () { return __awaiter(_this, void 0, void 0, function () {
        var error_4;
        var _this = this;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    setIsRefreshing(true);
                    _a.label = 1;
                case 1:
                    _a.trys.push([1, 3, 4, 5]);
                    return [4 /*yield*/, (0, socialbu_api_1.withErrorHandling)(function () { return __awaiter(_this, void 0, void 0, function () {
                            var api, accounts;
                            return __generator(this, function (_a) {
                                switch (_a.label) {
                                    case 0:
                                        api = (0, socialbu_api_1.getSocialBuAPI)();
                                        return [4 /*yield*/, api.getAccounts()];
                                    case 1:
                                        accounts = _a.sent();
                                        setConnectedAccounts(accounts);
                                        setHasError(accounts.some(function (account) { return account.status === "token_expired" || account.status === "error"; }));
                                        return [2 /*return*/];
                                }
                            });
                        }); }, "Failed to fetch connected accounts")];
                case 2:
                    _a.sent();
                    return [3 /*break*/, 5];
                case 3:
                    error_4 = _a.sent();
                    console.error("Error fetching accounts:", error_4);
                    return [3 /*break*/, 5];
                case 4:
                    setIsRefreshing(false);
                    return [7 /*endfinally*/];
                case 5: return [2 /*return*/];
            }
        });
    }); };
    // Disconnect an account
    var disconnectAccount = function (accountId) { return __awaiter(_this, void 0, void 0, function () {
        var error_5;
        var _this = this;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    _a.trys.push([0, 2, , 3]);
                    return [4 /*yield*/, (0, socialbu_api_1.withErrorHandling)(function () { return __awaiter(_this, void 0, void 0, function () {
                            var api;
                            return __generator(this, function (_a) {
                                switch (_a.label) {
                                    case 0:
                                        api = (0, socialbu_api_1.getSocialBuAPI)();
                                        return [4 /*yield*/, api.disconnectAccount(accountId)];
                                    case 1:
                                        _a.sent();
                                        toast({
                                            title: "Account disconnected",
                                            description: "The account has been successfully disconnected.",
                                        });
                                        // Refresh accounts list
                                        fetchAccounts();
                                        return [2 /*return*/];
                                }
                            });
                        }); }, "Failed to disconnect account")];
                case 1:
                    _a.sent();
                    return [3 /*break*/, 3];
                case 2:
                    error_5 = _a.sent();
                    console.error("Error disconnecting account:", error_5);
                    return [3 /*break*/, 3];
                case 3: return [2 /*return*/];
            }
        });
    }); };
    // Fetch accounts and check token on component mount
    (0, react_1.useEffect)(function () {
        checkUserToken();
        fetchAccounts();
    }, []);
    var availablePlatforms = [
        {
            name: "TikTok",
            platform: "tiktok",
            description: "Share short-form videos to your TikTok account",
            popular: true,
        },
        {
            name: "YouTube",
            platform: "youtube",
            description: "Manage your YouTube channel and video content",
            popular: true,
        },
        {
            name: "Pinterest",
            platform: "pinterest",
            description: "Share pins and manage your Pinterest boards",
            popular: false,
        },
    ];
    // Function to initiate OAuth flow for connecting a new account
    var connectAccount = function (platform) { return __awaiter(_this, void 0, void 0, function () {
        var api, result, error_6;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    // Check if user has token first
                    if (!hasToken) {
                        setIsAuthDialogOpen(true);
                        setAuthType("register");
                        return [2 /*return*/];
                    }
                    _a.label = 1;
                case 1:
                    _a.trys.push([1, 3, , 4]);
                    toast({
                        title: "Connecting account",
                        description: "Initiating connection to ".concat(platform, "..."),
                    });
                    api = (0, socialbu_api_1.getSocialBuAPI)();
                    return [4 /*yield*/, api.openConnectionPopup(platform)];
                case 2:
                    result = _a.sent();
                    toast({
                        title: "Account connected",
                        description: "Successfully connected to ".concat(result.accountName),
                    });
                    // Refresh accounts list
                    fetchAccounts();
                    return [3 /*break*/, 4];
                case 3:
                    error_6 = _a.sent();
                    console.error("Error connecting account:", error_6);
                    toast({
                        title: "Connection failed",
                        description: error_6 instanceof Error ? error_6.message : "Failed to connect account",
                        variant: "destructive",
                    });
                    return [3 /*break*/, 4];
                case 4: return [2 /*return*/];
            }
        });
    }); };
    // Auth modal content based on type (register or login)
    var renderAuthContent = function () {
        if (authType === "register") {
            return (<>
          <div className="space-y-4 py-2">
            <div className="space-y-2">
              <label_1.Label htmlFor="name">Name</label_1.Label>
              <input_1.Input id="name" name="name" value={authForm.name} onChange={handleAuthFormChange} placeholder="Your name"/>
            </div>
            <div className="space-y-2">
              <label_1.Label htmlFor="email">Email</label_1.Label>
              <input_1.Input id="email" name="email" type="email" value={authForm.email} onChange={handleAuthFormChange} placeholder="your.email@example.com"/>
            </div>
            <div className="space-y-2">
              <label_1.Label htmlFor="password">Password</label_1.Label>
              <input_1.Input id="password" name="password" type="password" value={authForm.password} onChange={handleAuthFormChange} placeholder="••••••••"/>
            </div>
            <div className="space-y-2">
              <label_1.Label htmlFor="retypePassword">Retype Password</label_1.Label>
              <input_1.Input id="retypePassword" name="retypePassword" type="password" value={authForm.retypePassword} onChange={handleAuthFormChange} placeholder="••••••••"/>
            </div>
          </div>
          <dialog_1.DialogFooter className="flex flex-col sm:flex-row sm:justify-between items-center gap-2 mt-4">
            <div>
              <span className="text-sm text-muted-foreground mr-2">Already registered?</span>
              <button_1.Button variant="link" className="px-0" onClick={function () { return setAuthType("login"); }}>Log In</button_1.Button>
            </div>
            <button_1.Button onClick={handleRegister}>Register</button_1.Button>
          </dialog_1.DialogFooter>
        </>);
        }
        else {
            return (<>
          <div className="space-y-4 py-2">
            <div className="space-y-2">
              <label_1.Label htmlFor="email">Email</label_1.Label>
              <input_1.Input id="email" name="email" type="email" value={authForm.email} onChange={handleAuthFormChange} placeholder="your.email@example.com"/>
            </div>
            <div className="space-y-2">
              <label_1.Label htmlFor="password">Password</label_1.Label>
              <input_1.Input id="password" name="password" type="password" value={authForm.password} onChange={handleAuthFormChange} placeholder="••••••••"/>
            </div>
          </div>
          <dialog_1.DialogFooter className="flex flex-col sm:flex-row sm:justify-between items-center gap-2 mt-4">
            <div>
              <span className="text-sm text-muted-foreground mr-2">Don't have an account?</span>
              <button_1.Button variant="link" className="px-0" onClick={function () { return setAuthType("register"); }}>Sign Up</button_1.Button>
            </div>
            <button_1.Button onClick={handleLogin}>Log In</button_1.Button>
          </dialog_1.DialogFooter>
        </>);
        }
    };
    return (<div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Platform Connect</h2>
          <p className="text-muted-foreground">Connect and manage your social media accounts</p>
        </div>
        <div className="flex items-center gap-2">
          {!hasToken && (<button_1.Button onClick={function () {
                setIsAuthDialogOpen(true);
                setAuthType("login");
            }}>
              <lucide_react_1.LogIn className="mr-2 h-4 w-4"/>
              Authorize SocialBu
            </button_1.Button>)}
          <button_1.Button variant="outline" onClick={fetchAccounts} disabled={isRefreshing}>
            {isRefreshing ? (<lucide_react_1.RefreshCw className="mr-2 h-4 w-4 animate-spin"/>) : (<lucide_react_1.RefreshCw className="mr-2 h-4 w-4"/>)}
            Refresh Connections
          </button_1.Button>
          <mode_toggle_1.ModeToggle />
        </div>
      </div>

      {/* SocialBu Auth Dialog */}
      <dialog_1.Dialog open={isAuthDialogOpen} onOpenChange={setIsAuthDialogOpen}>
        <dialog_1.DialogContent>
          <dialog_1.DialogHeader>
            <dialog_1.DialogTitle>{authType === "register" ? "Register with SocialBu" : "Authorize SocialBu"}</dialog_1.DialogTitle>
            <dialog_1.DialogDescription>
              {authType === "register"
            ? "Create a SocialBu account to connect your social media platforms."
            : "Log in to your SocialBu account to authorize access."}
            </dialog_1.DialogDescription>
          </dialog_1.DialogHeader>
          {renderAuthContent()}
        </dialog_1.DialogContent>
      </dialog_1.Dialog>

      {hasError && (<alert_1.Alert>
          <lucide_react_1.AlertCircle className="h-4 w-4"/>
          <alert_1.AlertTitle>Connection Status</alert_1.AlertTitle>
          <alert_1.AlertDescription>
            One or more of your connected accounts requires attention. Check the status below.
          </alert_1.AlertDescription>
        </alert_1.Alert>)}

      {!hasToken && (<alert_1.Alert variant="destructive">
          <lucide_react_1.AlertCircle className="h-4 w-4"/>
          <alert_1.AlertTitle>Authentication Required</alert_1.AlertTitle>
          <alert_1.AlertDescription>
            You need to register or log in to your SocialBu account to connect social media platforms.
          </alert_1.AlertDescription>
        </alert_1.Alert>)}

      <tabs_1.Tabs defaultValue="connected" value={activeTab} onValueChange={setActiveTab}>
        <tabs_1.TabsList>
          <tabs_1.TabsTrigger value="connected">Connected Platforms</tabs_1.TabsTrigger>
          <tabs_1.TabsTrigger value="available">Available Platforms</tabs_1.TabsTrigger>
        </tabs_1.TabsList>
        <tabs_1.TabsContent value="connected" className="space-y-4">
          {isRefreshing && connectedAccounts.length === 0 ? (<div className="flex justify-center p-8">
              <lucide_react_1.RefreshCw className="h-8 w-8 animate-spin text-muted-foreground"/>
            </div>) : connectedAccounts.length === 0 ? (<card_1.Card>
              <card_1.CardContent className="flex flex-col items-center justify-center p-8 text-center">
                <lucide_react_1.Link2 className="h-12 w-12 text-muted-foreground mb-4"/>
                <h3 className="text-lg font-medium">No Connected Platforms</h3>
                <p className="text-muted-foreground mt-2">
                  You haven't connected any social media platforms yet. Go to the "Available Platforms" tab to get
                  started.
                </p>
                <button_1.Button className="mt-4" onClick={function () { return setActiveTab("available"); }}>
                  Connect a Platform
                </button_1.Button>
              </card_1.CardContent>
            </card_1.Card>) : (<div className="grid gap-4 md:grid-cols-2">
              {connectedAccounts.map(function (account) {
                var platform = platformConfig[account.platform] || { icon: lucide_react_1.Link2, color: "#666" };
                var PlatformIcon = platform.icon;
                return (<card_1.Card key={account.id}>
                    <card_1.CardHeader className="pb-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="flex h-8 w-8 items-center justify-center rounded-full" style={{ backgroundColor: platform.color }}>
                            <PlatformIcon className="h-4 w-4 text-white"/>
                          </div>
                          <div>
                            <card_1.CardTitle className="text-base">{account.name}</card_1.CardTitle>
                            <card_1.CardDescription>{account.platform}</card_1.CardDescription>
                          </div>
                        </div>
                        <div className="flex items-center">
                          {account.status !== "token_expired" && account.status !== "error" ? (<badge_1.Badge variant="outline" className="bg-green-50 text-green-700 dark:bg-green-900/20">
                              <lucide_react_1.CheckCircle2 className="mr-1 h-3 w-3"/>
                              Connected
                            </badge_1.Badge>) : (<badge_1.Badge variant="outline" className="bg-amber-50 text-amber-700 dark:bg-amber-900/20">
                              <lucide_react_1.AlertCircle className="mr-1 h-3 w-3"/>
                              Needs Attention
                            </badge_1.Badge>)}
                        </div>
                      </div>
                    </card_1.CardHeader>
                    <card_1.CardContent className="pb-2">
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div>
                          <span className="text-muted-foreground">Account Type:</span> {account.type || "Standard"}
                        </div>
                        <div>
                          <span className="text-muted-foreground">Connected:</span>{" "}
                          {account.connected_at ? new Date(account.connected_at).toLocaleDateString() : "Recently"}
                        </div>
                      </div>
                    </card_1.CardContent>
                    <card_1.CardFooter className="flex justify-between pt-2">
                      <dialog_1.Dialog>
                        <dialog_1.DialogTrigger asChild>
                          <button_1.Button variant="outline" size="sm">
                            <lucide_react_1.Settings className="mr-2 h-3.5 w-3.5"/>
                            Manage
                          </button_1.Button>
                        </dialog_1.DialogTrigger>
                        <dialog_1.DialogContent>
                          <dialog_1.DialogHeader>
                            <dialog_1.DialogTitle>Manage {account.name} Connection</dialog_1.DialogTitle>
                            <dialog_1.DialogDescription>Configure your connection settings and permissions</dialog_1.DialogDescription>
                          </dialog_1.DialogHeader>
                          <div className="space-y-4 py-4">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                <div className="flex h-8 w-8 items-center justify-center rounded-full" style={{ backgroundColor: platform.color }}>
                                  <PlatformIcon className="h-4 w-4 text-white"/>
                                </div>
                                <div>
                                  <div className="font-medium">{account.name}</div>
                                  <div className="text-sm text-muted-foreground">
                                    {account.type || "Standard Account"}
                                  </div>
                                </div>
                              </div>
                              {account.status !== "token_expired" && account.status !== "error" ? (<badge_1.Badge variant="outline" className="bg-green-50 text-green-700 dark:bg-green-900/20">
                                  <lucide_react_1.CheckCircle2 className="mr-1 h-3 w-3"/>
                                  Connected
                                </badge_1.Badge>) : (<badge_1.Badge variant="outline" className="bg-amber-50 text-amber-700 dark:bg-amber-900/20">
                                  <lucide_react_1.AlertCircle className="mr-1 h-3 w-3"/>
                                  Needs Attention
                                </badge_1.Badge>)}
                            </div>

                            <separator_1.Separator />

                            <div className="space-y-2">
                              <h4 className="font-medium">Permissions</h4>
                              <div className="space-y-2">
                                <div className="flex items-center justify-between">
                                  <label_1.Label htmlFor={"post-permission-".concat(account.id)} className="flex items-center gap-2">
                                    <span>Post Content</span>
                                    <lucide_react_1.Info className="h-3.5 w-3.5 text-muted-foreground"/>
                                  </label_1.Label>
                                  <switch_1.Switch id={"post-permission-".concat(account.id)} defaultChecked/>
                                </div>
                                <div className="flex items-center justify-between">
                                  <label_1.Label htmlFor={"read-permission-".concat(account.id)} className="flex items-center gap-2">
                                    <span>Read Content</span>
                                    <lucide_react_1.Info className="h-3.5 w-3.5 text-muted-foreground"/>
                                  </label_1.Label>
                                  <switch_1.Switch id={"read-permission-".concat(account.id)} defaultChecked/>
                                </div>
                                <div className="flex items-center justify-between">
                                  <label_1.Label htmlFor={"insights-permission-".concat(account.id)} className="flex items-center gap-2">
                                    <span>Access Insights</span>
                                    <lucide_react_1.Info className="h-3.5 w-3.5 text-muted-foreground"/>
                                  </label_1.Label>
                                  <switch_1.Switch id={"insights-permission-".concat(account.id)} defaultChecked/>
                                </div>
                              </div>
                            </div>

                            <separator_1.Separator />

                            <div className="space-y-2">
                              <h4 className="font-medium">Account Settings</h4>
                              <div className="space-y-2">
                                <div className="flex items-center justify-between">
                                  <label_1.Label htmlFor={"auto-sync-".concat(account.id)} className="flex items-center gap-2">
                                    <span>Auto-sync content</span>
                                  </label_1.Label>
                                  <switch_1.Switch id={"auto-sync-".concat(account.id)} defaultChecked/>
                                </div>
                                <div className="flex items-center justify-between">
                                  <label_1.Label htmlFor={"notifications-".concat(account.id)} className="flex items-center gap-2">
                                    <span>Receive notifications</span>
                                  </label_1.Label>
                                  <switch_1.Switch id={"notifications-".concat(account.id)} defaultChecked/>
                                </div>
                              </div>
                            </div>
                          </div>
                          <dialog_1.DialogFooter className="flex items-center justify-between">
                            <button_1.Button variant="destructive" size="sm" onClick={function () {
                        var _a;
                        disconnectAccount(account.id);
                        (_a = document
                            .querySelector('[data-state="open"] button[aria-label="Close"]')) === null || _a === void 0 ? void 0 : _a.dispatchEvent(new MouseEvent("click", { bubbles: true }));
                    }}>
                              <lucide_react_1.Trash2 className="mr-2 h-3.5 w-3.5"/>
                              Disconnect
                            </button_1.Button>
                            <div className="flex gap-2">
                              <button_1.Button variant="outline">Cancel</button_1.Button>
                              <button_1.Button>Save Changes</button_1.Button>
                            </div>
                          </dialog_1.DialogFooter>
                        </dialog_1.DialogContent>
                      </dialog_1.Dialog>

                      <dropdown_menu_1.DropdownMenu>
                        <dropdown_menu_1.DropdownMenuTrigger asChild>
                          <button_1.Button variant="ghost" size="sm">
                            <lucide_react_1.Settings className="h-3.5 w-3.5"/>
                            <span className="sr-only">More options</span>
                          </button_1.Button>
                        </dropdown_menu_1.DropdownMenuTrigger>
                        <dropdown_menu_1.DropdownMenuContent align="end">
                          <dropdown_menu_1.DropdownMenuLabel>Options</dropdown_menu_1.DropdownMenuLabel>
                          <dropdown_menu_1.DropdownMenuSeparator />
                          <dropdown_menu_1.DropdownMenuItem>
                            <lucide_react_1.RefreshCw className="mr-2 h-3.5 w-3.5"/>
                            Refresh Token
                          </dropdown_menu_1.DropdownMenuItem>
                          <dropdown_menu_1.DropdownMenuItem>
                            <lucide_react_1.ExternalLink className="mr-2 h-3.5 w-3.5"/>
                            View Profile
                          </dropdown_menu_1.DropdownMenuItem>
                          <dropdown_menu_1.DropdownMenuSeparator />
                          <dropdown_menu_1.DropdownMenuItem className="text-destructive" onClick={function () { return disconnectAccount(account.id); }}>
                            <lucide_react_1.Trash2 className="mr-2 h-3.5 w-3.5"/>
                            Disconnect
                          </dropdown_menu_1.DropdownMenuItem>
                        </dropdown_menu_1.DropdownMenuContent>
                      </dropdown_menu_1.DropdownMenu>
                    </card_1.CardFooter>
                  </card_1.Card>);
            })}
            </div>)}
        </tabs_1.TabsContent>
        <tabs_1.TabsContent value="available" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-3">
            {availablePlatforms.map(function (platform) {
            var platformInfo = platformConfig[platform.platform] || { icon: lucide_react_1.Link2, color: "#666" };
            var PlatformIcon = platformInfo.icon;
            return (<card_1.Card key={platform.name} className="overflow-hidden">
                  <card_1.CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className="flex h-8 w-8 items-center justify-center rounded-full" style={{ backgroundColor: platformInfo.color }}>
                          <PlatformIcon className="h-4 w-4 text-white"/>
                        </div>
                        <card_1.CardTitle className="text-base">{platform.name}</card_1.CardTitle>
                      </div>
                      {platform.popular && (<badge_1.Badge variant="secondary" className="bg-primary/10 text-primary">
                          Popular
                        </badge_1.Badge>)}
                    </div>
                  </card_1.CardHeader>
                  <card_1.CardContent className="pb-2">
                    <p className="text-sm text-muted-foreground">{platform.description}</p>
                  </card_1.CardContent>
                  <card_1.CardFooter className="pt-2">
                    <button_1.Button className="w-full" onClick={function () { return connectAccount(platform.platform); }}>
                      <lucide_react_1.Plus className="mr-2 h-3.5 w-3.5"/>
                      Connect
                    </button_1.Button>
                  </card_1.CardFooter>
                </card_1.Card>);
        })}

            <card_1.Card className="overflow-hidden border-dashed">
              <card_1.CardHeader className="pb-2">
                <div className="flex items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-muted">
                    <lucide_react_1.Link2 className="h-4 w-4"/>
                  </div>
                  <card_1.CardTitle className="text-base">Request Platform</card_1.CardTitle>
                </div>
              </card_1.CardHeader>
              <card_1.CardContent className="pb-2">
                <p className="text-sm text-muted-foreground">
                  Don't see the platform you need? Request a new integration.
                </p>
              </card_1.CardContent>
              <card_1.CardFooter className="pt-2">
                <button_1.Button variant="outline" className="w-full">
                  Request Platform
                </button_1.Button>
              </card_1.CardFooter>
            </card_1.Card>
          </div>
        </tabs_1.TabsContent>
      </tabs_1.Tabs>

      <card_1.Card>
        <card_1.CardHeader>
          <card_1.CardTitle>Connection Settings</card_1.CardTitle>
          <card_1.CardDescription>Manage global settings for all connected platforms</card_1.CardDescription>
        </card_1.CardHeader>
        <card_1.CardContent className="space-y-4">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <label_1.Label htmlFor="auto-refresh">Auto-refresh tokens</label_1.Label>
                <p className="text-sm text-muted-foreground">
                  Automatically refresh connection tokens before they expire
                </p>
              </div>
              <switch_1.Switch id="auto-refresh" defaultChecked/>
            </div>
            <separator_1.Separator />
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <label_1.Label htmlFor="sync-profiles">Sync profile changes</label_1.Label>
                <p className="text-sm text-muted-foreground">Keep your profile information in sync across platforms</p>
              </div>
              <switch_1.Switch id="sync-profiles"/>
            </div>
            <separator_1.Separator />
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <label_1.Label htmlFor="connection-notifications">Connection notifications</label_1.Label>
                <p className="text-sm text-muted-foreground">Receive notifications about connection status changes</p>
              </div>
              <switch_1.Switch id="connection-notifications" defaultChecked/>
            </div>
          </div>
        </card_1.CardContent>
      </card_1.Card>
    </div>);
}

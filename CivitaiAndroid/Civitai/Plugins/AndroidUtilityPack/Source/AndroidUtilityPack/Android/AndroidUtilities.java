// Copyright Porret Gaming 2024, All Rights Reserved
package com.porretgaming.androidutilitypack;

import android.app.Activity;

import android.content.Intent;
import android.content.IntentFilter;

import android.os.BatteryManager;
import android.os.Build;
import android.util.Log;

import android.net.ConnectivityManager;
import android.net.Network;
import android.net.NetworkCapabilities;
import android.net.NetworkInfo;
import android.net.NetworkRequest;

import java.net.HttpURLConnection;
import java.net.URL;

import java.io.IOException;

import java.lang.Integer;
import java.util.ArrayList;
import java.util.List;

public class AndroidUtilities
{
    /* Core Variables */    
    private final Activity mGameActivity;
    private String mURLTest = "https://clients3.google.com/generate_204";
    private int mConnectionTimeout = 1500;
    
    private boolean LifeCycleEventsSetup = false;
    private List<Integer> mLifeCycleEvents = new ArrayList<Integer>();

    private ConnectivityManager connectivityManager;
    private ConnectivityManager.NetworkCallback networkCallback;
    private boolean NetworkCallbacksSetup = false;
    private boolean NetworkCallbacksRequested = false;
    private boolean LastInternetCheckResult = false;
    
    /* C++ Callbacks */
    public static native void CPPOnLifecycleEvent(int jEventType);
    public static native void CPPOnInternetStatusChanged(InternetCheckResult jNetworkEvent);

    /* Constructor */
    public AndroidUtilities(Activity GameActivity, String ConnectionURL, int ConnectionTimeout)
    {
        /*
            Configure Settings and Variables
        */
        mGameActivity = GameActivity;
        mURLTest = ConnectionURL;
        mConnectionTimeout = ConnectionTimeout;

        // Initialize connectivity manager and network callback
        connectivityManager = (ConnectivityManager) mGameActivity.getSystemService(Activity.CONNECTIVITY_SERVICE);
    }

    public void ADBLog(int LogLevel, String Tag, String Message) {
        switch(LogLevel) {
            // Verbose
            case 0:
                Log.v(Tag, Message);
                break;
            // Debug
            case 1:
                Log.d(Tag, Message);
                break;
            // Info
            case 2:
                Log.i(Tag, Message);
                break;
            // Warning
            case 3:
                Log.w(Tag, Message);
                break;
            // Error
            default:
                Log.e(Tag, Message);
                break;
        }
    }

    public void OnLifecycleEvent(int LifeCycleType) {
        if (LifeCycleEventsSetup) {
            CPPOnLifecycleEvent(LifeCycleType);
        } else {
            mLifeCycleEvents.add(LifeCycleType);
        }
    }

    public void SetupLifeCycleEventCallback() {
        LifeCycleEventsSetup = true;

        for (Integer event : mLifeCycleEvents) {
            CPPOnLifecycleEvent(event);
        }

        mLifeCycleEvents.clear();
    }

    public int GetAndroidSDKVersion() {
        return Build.VERSION.SDK_INT;
    }

    public AndroidBatteryInfo GetCurrentBatteryStatus() {
        IntentFilter ifilter = new IntentFilter(Intent.ACTION_BATTERY_CHANGED);
        Intent batteryStatus = Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU ? mGameActivity.registerReceiver(null, ifilter, mGameActivity.RECEIVER_EXPORTED) : mGameActivity.registerReceiver(null, ifilter);

        // Calculate Battery Percentage
        int level = batteryStatus.getIntExtra(BatteryManager.EXTRA_LEVEL, -1); // API 5
        int scale = batteryStatus.getIntExtra(BatteryManager.EXTRA_SCALE, -1); // API 5
        float batteryPct = level / (float) scale * 100;

        int status = batteryStatus.getIntExtra(BatteryManager.EXTRA_STATUS, -1); // API 5
        int health = batteryStatus.getIntExtra(BatteryManager.EXTRA_HEALTH, -1); // API 5
        int plugType = batteryStatus.getIntExtra(BatteryManager.EXTRA_PLUGGED, -1); // API 5
        int temperature = batteryStatus.getIntExtra(BatteryManager.EXTRA_TEMPERATURE, -1); // API 5
        int voltage = batteryStatus.getIntExtra(BatteryManager.EXTRA_VOLTAGE, -1); // API 5
        String technology = batteryStatus.getStringExtra(BatteryManager.EXTRA_TECHNOLOGY); // API 5
        boolean isBatteryLow = Build.VERSION.SDK_INT >= Build.VERSION_CODES.P ? batteryStatus.getBooleanExtra(BatteryManager.EXTRA_BATTERY_LOW, false) : false; // API 28
        boolean isBatteryPresent = batteryStatus.getBooleanExtra(BatteryManager.EXTRA_PRESENT, false); // API 5
        
        return new AndroidBatteryInfo(
            status,
            batteryPct,
            isBatteryLow,
            isBatteryPresent,
            health,
            plugType,
            temperature / 10.0f,
            voltage,
            technology);
    }

    public InternetCheckResult IsConnectedToInternet() {
        if (connectivityManager != null) {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                NetworkCapabilities capabilities = connectivityManager.getNetworkCapabilities(connectivityManager.getActiveNetwork());
                if (capabilities != null) {
                    if (capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) ||
                        capabilities.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) ||
                        capabilities.hasTransport(NetworkCapabilities.TRANSPORT_ETHERNET)) {
                        InternetCheckResult Result = isInternetAvailable();
                        LastInternetCheckResult = Result.getIsConnected();
                        return Result;
                    } else {
                        LastInternetCheckResult = false;
                        return new InternetCheckResult(false, "No Valid Network Capabilities");
                    }
                } else {
                    LastInternetCheckResult = false;
                    return new InternetCheckResult(false, "No Network Capabilities Present");
                }
            } else {
                NetworkInfo activeNetwork = connectivityManager.getActiveNetworkInfo();
                if (activeNetwork != null && activeNetwork.isConnected()) {
                    InternetCheckResult Result = isInternetAvailable();
                    LastInternetCheckResult = Result.getIsConnected();
                    return Result;
                } else {
                    LastInternetCheckResult = false;
                    return new InternetCheckResult(false, "No Actively Connected Network");
                }
            }
        }
        LastInternetCheckResult = false;
        return new InternetCheckResult(false, "Cannot Retrieve Connectivity Manager");
    }

    public void SetupNetworkCallbacks() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            NetworkCallbacksRequested = true;
            BuildUpNetworkCallbacks();
        }
    }

    /* Internal Lifecycle Event Use */
    public void BuildUpNetworkCallbacks() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP && NetworkCallbacksRequested && !NetworkCallbacksSetup) {
            networkCallback = new ConnectivityManager.NetworkCallback() {
                @Override
                public void onAvailable(Network network) {
                    // Network is available, check internet connectivity
                    InternetCheckResult Result = isInternetAvailable();
                    if (!Result.getIsConnected() || LastInternetCheckResult != Result.getIsConnected()) {
                        LastInternetCheckResult = Result.getIsConnected();
                        CPPOnInternetStatusChanged(Result);
                    }
                }

                @Override
                public void onLost(Network network) {
                    // Network is lost
                    LastInternetCheckResult = false;
                    CPPOnInternetStatusChanged(new InternetCheckResult(false, "Network Connectivity Lost"));
                }
            };

            NetworkRequest networkRequest = new NetworkRequest.Builder()
                    .addCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
                    .build();

            connectivityManager.registerNetworkCallback(networkRequest, networkCallback);
            NetworkCallbacksSetup = true;
        }
    }

    public void TearDownNetworkCallbacks() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP && NetworkCallbacksSetup) {
            connectivityManager.unregisterNetworkCallback(networkCallback);
            NetworkCallbacksSetup = false;
        }
    }

    public void CheckInternetChangedOnResume() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP && NetworkCallbacksRequested && NetworkCallbacksSetup) {
            InternetCheckResult ConnectionStatus = isInternetAvailable();

            if (!ConnectionStatus.getIsConnected() && LastInternetCheckResult) {
                LastInternetCheckResult = false;
                CPPOnInternetStatusChanged(new InternetCheckResult(false, "Network Connectivity Lost"));
            }
        }
    }

    private InternetCheckResult isInternetAvailable() {
        try {
            HttpURLConnection urlConnection = (HttpURLConnection) 
                    (new URL(mURLTest)
                    .openConnection());
            urlConnection.setRequestProperty("User-Agent", "Android");
            urlConnection.setRequestProperty("Connection", "close");
            urlConnection.setConnectTimeout(mConnectionTimeout);
            urlConnection.connect();
            boolean result = (urlConnection.getResponseCode() == 204 && urlConnection.getContentLength() == 0);
            return new InternetCheckResult(result, result ? "" : "Cannot reach '" + mURLTest + "'");
        } catch (IOException e) {
            return new InternetCheckResult(false, e.getMessage());
        }
    }


}
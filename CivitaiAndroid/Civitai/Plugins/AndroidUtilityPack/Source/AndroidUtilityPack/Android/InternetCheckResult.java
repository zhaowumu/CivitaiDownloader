// Copyright Porret Gaming 2024, All Rights Reserved
package com.porretgaming.androidutilitypack;

public class InternetCheckResult
{
    private final boolean IsConnected;
    private final String FailureReason;

    public InternetCheckResult(
        boolean _IsConnected,
        String _FailureReason)
    {
        IsConnected = _IsConnected;
        FailureReason = _FailureReason;
    }

    public boolean getIsConnected() {
        return IsConnected;
    }

    public String getFailureReason() {
        return FailureReason;
    }
}
"use client";

import React, { createContext, useContext, useState } from 'react';

interface TenantContextType {
  clientId: string;
}

const MOCK_TENANT_DATA = {
  clientId: 'playground-ia',
};

const TenantContext = createContext<TenantContextType | undefined>(undefined);

export function TenantProvider({ children }: { children: React.ReactNode }) {
  const [tenantData] = useState<TenantContextType>({
    clientId: MOCK_TENANT_DATA.clientId,
  });

  return (
    <TenantContext.Provider value={tenantData}>
      {children}
    </TenantContext.Provider>
  );
}

export function useTenant() {
  const context = useContext(TenantContext);
  if (context === undefined) {
    throw new Error('useTenant must be used within a TenantProvider');
  }
  return context;
}
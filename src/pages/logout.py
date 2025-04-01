from nicegui import ui

@ui.page('/logout')
def logout():
    # 1. Clear your app's session
    ui.run_javascript('localStorage.removeItem("myapp_wallet_address")')
    
    # 2. Tell MetaMask to disconnect (they may ignore this)
    ui.run_javascript("""
        if (window.ethereum?.isMetaMask) {
            // This just asks nicely - MetaMask may not comply
            window.ethereum.request({
                method: 'wallet_revokePermissions',
                params: [{ eth_accounts: {} }]
            }).catch(() => {});
        }
    """)
    
    # 3. Show logout message
    ui.label("You're logged out (but MetaMask may still be connected)")
    ui.button("Back to home", on_click=lambda: ui.navigate.to('/'))
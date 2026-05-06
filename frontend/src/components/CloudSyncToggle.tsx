import { useFinance } from "@/context/FinanceContext";
import { allowCloudSync, isCloudSyncAllowed } from "@/lib/offline";
import React from "react";


export function CloudSyncToggle() {

  const [loading, setLoading] = React.useState(false);

  const [enabled, setEnabled] = React.useState(isCloudSyncAllowed());

  const { triggerCloudSync, triggerRemoveCloudData } = useFinance();

  const onToggle = async (newState: boolean) => {
    allowCloudSync(newState);

    // Sync the cloud or delete cloud data depending on new state

    setLoading(true);

    if (newState) {
      // Sync the cloud
      triggerCloudSync().finally(() => setLoading(false));
    } else {
      // Delete cloud data
      triggerRemoveCloudData().finally(() => setLoading(false));
    }

    setEnabled(newState);

    setLoading(false);
  }

  return (
    <div className="flex items-center">
      <label htmlFor="cloud-sync-toggle" className="mr-4 text-gray-700 dark:text-neutral-300">
        Cloud Sync
      </label>
      <button
        id="cloud-sync-toggle"
        onClick={() => {
          if (loading) return;
          if (enabled) {
            // Confirm disabling cloud sync
            if (confirm("Are you sure you want to disable cloud sync? Your data will no longer be backed up to the cloud.")) {
              onToggle(false);
            }
          } else {
            onToggle(true);
          }
        }}
        disabled={loading}
        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none ${enabled ? 'bg-blue-600' : 'bg-gray-300 dark:bg-neutral-600'
          } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <span
          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${enabled ? 'translate-x-5' : 'translate-x-1'
            } ${loading ? 'animate-pulse' : ''}`}
        />
      </button>
    </div>
  );
}

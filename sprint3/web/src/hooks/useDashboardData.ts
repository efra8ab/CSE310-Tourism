import { useCallback, useEffect, useState } from "react";
import { buildMockDashboard, fetchDashboard } from "../api/dashboard";
import { DashboardData, DashboardFilters } from "../types";

export const useDashboardData = (
  initialFilters: DashboardFilters,
  limit = 5
) => {
  const [filters, setFilters] = useState<DashboardFilters>(initialFilters);
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(
    async (nextFilters: DashboardFilters = filters) => {
      setLoading(true);
      setError(null);
      try {
        const payload = await fetchDashboard(nextFilters, limit);
        setData(payload);
      } catch (err) {
        console.error(err);
        try {
          const mock = buildMockDashboard(nextFilters, limit);
          setData(mock);
          setError(
            err instanceof Error
              ? `${err.message} (showing mock data)`
              : "Showing mock data."
          );
        } catch (mockErr) {
          setError(
            mockErr instanceof Error
              ? mockErr.message
              : "Unable to load dashboard data."
          );
        }
      } finally {
        setLoading(false);
      }
    },
    [filters, limit]
  );

  useEffect(() => {
    load(filters);
  }, [filters, load]);

  return {
    data,
    loading,
    error,
    filters,
    setFilters,
    refresh: () => load(filters),
  };
};

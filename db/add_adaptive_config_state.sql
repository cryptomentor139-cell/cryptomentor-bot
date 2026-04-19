-- Adaptive Confluence Global State (single-row table)

CREATE TABLE IF NOT EXISTS public.adaptive_config_state (
  id                                integer PRIMARY KEY DEFAULT 1,
  mode                              text NOT NULL DEFAULT 'balanced',
  conf_delta                        integer NOT NULL DEFAULT 0,
  volume_min_ratio_delta            numeric(8,4) NOT NULL DEFAULT 0.0,
  ob_fvg_requirement_mode           text NOT NULL DEFAULT 'soft',
  strategy_loss_rate                numeric(8,6) NOT NULL DEFAULT 0.0,
  entry_without_ob_fvg_loss_share   numeric(8,6) NOT NULL DEFAULT 0.0,
  entry_without_volume_loss_share   numeric(8,6) NOT NULL DEFAULT 0.0,
  trade_count_per_day               numeric(10,6) NOT NULL DEFAULT 0.0,
  strategy_sample_size              integer NOT NULL DEFAULT 0,
  ops_reconcile_rate                numeric(8,6) NOT NULL DEFAULT 0.0,
  baseline_loss_rate                numeric(8,6),
  baseline_trade_count_per_day      numeric(10,6),
  target_loss_lower                 numeric(8,6),
  target_loss_upper                 numeric(8,6),
  decision_reason                   text,
  last_adapted_at                   timestamptz,
  updated_at                        timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_adaptive_config_state_updated_at
  ON public.adaptive_config_state(updated_at DESC);

-- Ensure singleton row exists
INSERT INTO public.adaptive_config_state (id)
VALUES (1)
ON CONFLICT (id) DO NOTHING;


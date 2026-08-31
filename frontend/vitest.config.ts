import { defineConfig } from 'vitest/config';

/**
 * Run the spec files one at a time.
 *
 * Booting a second Vitest worker pulls the whole Angular + Material bundle
 * into a fresh process; on a loaded machine that exceeds the 60 s worker
 * handshake and the run dies with "Timeout waiting for worker to respond"
 * before a single test executes (measured locally, both files passing alone).
 * The suite is small - serial execution costs seconds and never flakes.
 */
export default defineConfig({
  test: {
    pool: 'forks',
    poolOptions: { forks: { singleFork: true } },
  },
});

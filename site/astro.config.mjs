// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
  site: 'https://srebudo.ai',
  integrations: [
    starlight({
      title: 'srebudo.ai',
      description:
        'The way of the SRE agent — a hands-on dojo for building AI agents that solve real platform problems.',
      customCss: ['./src/styles/custom.css'],
      social: {
        github: 'https://github.com/your-org/srebudo.ai',
      },
      sidebar: [
        { label: 'The Way of Budo', slug: 'manifesto' },
        {
          label: 'Foundations',
          items: [
            { label: 'Ch0 — The Dojo (lab setup)', slug: 'ch00-dojo' },
            { label: 'Ch1 — The Naked Loop ⬜', slug: 'ch01-naked-loop' },
          ],
        },
        {
          label: 'The Belts',
          items: [
            { label: 'Ch2 — IaC 🟨', slug: 'ch02-iac' },
            { label: 'Ch3 — CI/CD 🟧', slug: 'ch03-cicd' },
            { label: 'Ch4 — Observability 🟩', slug: 'ch04-observability' },
            { label: 'Ch5 — Oncall 🟦', slug: 'ch05-oncall' },
            { label: 'Ch6 — Scale 🟪', slug: 'ch06-scale' },
            { label: 'Ch7 — Cost 🟫', slug: 'ch07-cost' },
            { label: 'Ch8 — Security 🟥', slug: 'ch08-security' },
          ],
        },
        { label: 'Ch9 — Black Belt: the budo CLI ⬛', slug: 'ch09-capstone' },
        { label: 'Appendix: Local Models', slug: 'appendix-local-models' },
      ],
    }),
  ],
});

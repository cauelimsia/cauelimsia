<div align="center">

<img src="assets/banner.png" width="900" alt="Cauê Lima — desenvolvedor full-stack, Manaus AM, disponível para remoto">

Levo produto do schema ao domínio no ar: modelagem de dados, API, interface e deploy.
A maior parte do que construí está em produção hoje, atendendo usuário real —
sistemas de saúde suplementar, CRM e captação de leads.

<a href="https://cauedev.shop"><img width="175" src="https://img.shields.io/badge/cauedev.shop-125CFE?style=flat&logo=googlechrome&logoColor=white" alt="cauedev.shop"></a>
<a href="mailto:clsolucoesweb@gmail.com"><img width="107" src="https://img.shields.io/badge/E--mail-EA4335?style=flat&logo=gmail&logoColor=white" alt="E-mail"></a>

</div>

---

## 🧱 Stack

<div align="center">

<img width="148" src="https://img.shields.io/badge/TypeScript-3178C6?style=flat&logo=typescript&logoColor=white" alt="TypeScript">
<img width="144" src="https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black" alt="JavaScript">
<img width="117" src="https://img.shields.io/badge/Node.js-5FA04E?style=flat&logo=nodedotjs&logoColor=white" alt="Node.js">
<img width="155" src="https://img.shields.io/badge/PostgreSQL-4169E1?style=flat&logo=postgresql&logoColor=white" alt="PostgreSQL">

<img width="114" src="https://img.shields.io/badge/Next.js-000000?style=flat&logo=nextdotjs&logoColor=white" alt="Next.js">
<img width="131" src="https://img.shields.io/badge/React_19-61DAFB?style=flat&logo=react&logoColor=black" alt="React 19">
<img width="124" src="https://img.shields.io/badge/Tailwind-06B6D4?style=flat&logo=tailwindcss&logoColor=white" alt="Tailwind CSS">
<img width="121" src="https://img.shields.io/badge/three.js-000000?style=flat&logo=threedotjs&logoColor=white" alt="three.js">

<img width="138" src="https://img.shields.io/badge/Supabase-3FCF8E?style=flat&logo=supabase&logoColor=white" alt="Supabase">
<img width="114" src="https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white" alt="Docker">
<img width="107" src="https://img.shields.io/badge/Vercel-000000?style=flat&logo=vercel&logoColor=white" alt="Vercel">
<img width="141" src="https://img.shields.io/badge/Linux_VPS-FCC624?style=flat&logo=linux&logoColor=black" alt="Linux VPS">

</div>

| | |
|---|---|
| **Linguagens** | TypeScript, JavaScript, SQL / PL-pgSQL |
| **Front** | Next.js (App Router), React 19, Tailwind CSS, three.js, PWA |
| **Back** | Node.js, rotas de API Next, Postgres, Supabase (RLS) |
| **Dados** | ETL em Node sobre datasets públicos, modelagem e RPCs em Postgres |
| **Infra** | Vercel, Netlify, VPS Linux com Docker, GitHub Pages |
| **Também** | Meta Ads e mensuração — construo o funil e também leio o resultado dele |

---

## 🚀 Em produção

| Produto | O que é | Stack | Código |
|---|---|---|---|
| [**Pront.**](https://pront-saude-digital.netlify.app) | SaaS multi-tenant de saúde digital: prontuário eletrônico, agenda e gestão de clínicas, com isolamento por clínica via Row Level Security | Next.js 14 · TypeScript · Supabase | [público](https://github.com/cauelimsia/pront-saude-digital) |
| [**Rede Certa**](https://top-prime-rede.vercel.app) | Consulta de rede hospitalar por plano de saúde. ETL próprio sobre os dados abertos da ANS: ~40M de vínculos reduzidos a uma base consultável de ~66 mil planos e ~33 mil hospitais | Next.js 16 · Postgres · ETL em Node | privado |
| [**Top Prime Seguros**](https://topprimeseguros.com.br) | Site de captação de leads com atribuição de ponta a ponta e conformidade LGPD/Google Ads | Next.js · Supabase | privado |
| [**Cotador**](https://top-prime-cotador.vercel.app) | Gerador de cotações de plano de saúde em PDF, com múltiplos temas de marca | Next.js · Supabase | privado |
| [**DNIA**](https://dnia-site.vercel.app) | Site de produto para agente de IA em WhatsApp, com animação em three.js e GSAP | Next.js 16 · three.js · GSAP | privado |

---

## 📂 Repositórios públicos

| Repo | O que tem de interessante |
|---|---|
| **[surebet-api](https://github.com/cauelimsia/surebet-api)** | Motor de arbitragem esportiva como função pura, worker que reconcilia estado em vez de acumular, e o detalhe de agrupamento de linha assinada que separa arbitragem real de fantasma. Monorepo pnpm com Vitest |
| **[pront-saude-digital](https://github.com/cauelimsia/pront-saude-digital)** | Multi-tenancy real: o isolamento entre clínicas está nas policies do Postgres, não na aplicação |
| **[redecorr-apresentacao](https://github.com/cauelimsia/redecorr-apresentacao)** | Deck em WebGL — uma nuvem de 2.800 partículas em three.js que muda de formação conforme a narrativa, com modo apresentador. JavaScript puro |
| **[plano-a-apresentacao](https://github.com/cauelimsia/plano-a-apresentacao)** | Engine de slides própria onde o conteúdo é dado: `index.html` tem 44 linhas, o resto é derivado |
| **[presentations](https://github.com/cauelimsia/presentations)** | Mesma engine, agora data-driven em ES modules |

> Boa parte do que trabalho é código de cliente e fica em repositório privado.
> Os links da tabela **Em produção** levam ao produto no ar, que é onde dá para ver o resultado.

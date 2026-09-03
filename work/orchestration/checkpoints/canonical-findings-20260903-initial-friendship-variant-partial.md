# Canonical finding checkpoint — Initial Friendship gauge variant

Claim: `canonical-findings-maintenance-auto11-20260903T092947Z`
Finding: `cf-13f41d397ec5e6ad`

Live finding evidence is category 155 Support Effect prose using `初始羁绊槽上升`, with suggested target `Initial Friendship`. The existing canonical community term `support.initial_friendship.effect155` already locks `Initial Friendship` for category 155 but only covered aliases `初始牵绊值` and `初始羁绊值`.

Durable changes on `main`:

- `b760b1ff9a819e3cce052f14b13758e09ab1ffb4` extends that existing scoped term with alias `初始羁绊槽上升`; scope remains `text_data_dict.json` + category `155`, so generic relationship prose stays excluded.
- `4767d2fc4cd3a7166baa583807953bdb2a3ebc3a` adds regression coverage proving the variant resolves to `Initial Friendship` under the same scoped rule.

Validation:

- local Shiro runtime does not include pytest, so repository GitHub Actions is the acceptance backend;
- Validate run `33739601304` was queued for the regression commit at checkpoint time; do not mark the finding complete until Validate passes and production Sync refresh resolves the finding in generated context.

/*
 * Copyright (c) 2018 ISP RAS (http://www.ispras.ru)
 * Ivannikov Institute for System Programming of the Russian Academy of Sciences
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#ifndef __LDV_VERIFIER_COMMON_H
#define __LDV_VERIFIER_COMMON_H

/* Alias for __VERIFIER_error(). Unconditionally reach error function call. */
extern void ldv_error(void);

/* Alias for __VERIFIER_assume(). Proceed only if expression is nonzero. */
/* TODO: CPAchecker can report timeouts instead of good verdicts and v.v. when __VERIFIER_assume() is invoked directly or through ldv_assume()
 * extern void ldv_assume(int expr);
 */
void __VERIFIER_assume(int expr);
#define ldv_assume(expr) __VERIFIER_assume(expr)

#endif /* __LDV_VERIFIER_COMMON_H */

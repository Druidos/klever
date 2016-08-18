/*
 * Copyright (c) 2014-2015 ISPRAS (http://www.ispras.ru)
 * Institute for System Programming of the Russian Academy of Sciences
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * ee the License for the specific language governing permissions and
 * limitations under the License.
 */

#include <linux/ldv/common.h>
#include <verifier/common.h>

int ldv_dma_calls = 0;

/* MODEL_FUNCTION_DEFINITION Map page */
void ldv_dma_map_page(void) {
	/* ASSERT Check that previous dma_mapping call was checked */
	ldv_assert("linux:dma::double map", ldv_dma_calls == 0);
	/* CHANGE_STATE Increase map counter */
	ldv_dma_calls++;
}

/* MODEL_FUNCTION_DEFINITION Unmap page */
void ldv_dma_mapping_error(void) {
	/* ASSERT No dma_mapping calls to verify */				
	ldv_assert("linux:dma::unmap before map", ldv_dma_calls > 0);
	ldv_dma_calls--;
}

/* MODEL_FUNC_DEF Map page */
void ldv_dma_map_single(void) {
	/* ASSERT Check that previous dma_mapping call was checked */
	ldv_assert("linux:dma::double map", ldv_dma_calls == 0);
	/* CHANGE_STATE Increase map counter */
	ldv_dma_calls++;
}
	
/* MODEL_FUNC_DEF Map page */
void ldv_dma_map_single_attrs(void) {
	/* ASSERT Check that previous dma_mapping call was checked */
	ldv_assert("linux:dma::double map", ldv_dma_calls == 0);
	/* CHANGE_STATE Increase map counter */
	ldv_dma_calls++;
}

/* MODEL_FUNC_DEF Check that all module reference counters have their initial values at the end */
void ldv_check_final_state(void) {
	/* ASSERT All incremented module reference counters should be decremented before module unloading*/
	ldv_assert("linux:dma::more initial at exit", ldv_dma_calls == 0);
}

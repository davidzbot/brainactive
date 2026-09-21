-- BrainActive HA QA round 2 (2026-09-21): round-2 rejects, option-fix holds, explanation repairs.
-- All touched rows end inactive except the 9 explanation repairs, which keep their active flag.

update public.brainactive_questions
set qa_status = 'rejected_too_simple', is_active = false, updated_at = now()
where id in ('BA_P3_0010', 'BA_P3_0036', 'BA_P3_0032', 'BA_P3_0077', 'BA_P3_0213', 'BA_P3_0218', 'BA_P3_0269', 'BA_P3_ADD_0044')
  and qa_status not like 'rejected%';

update public.brainactive_questions
set qa_status = 'needs_option_fix_20260921', is_active = false, updated_at = now()
where id in ('BA_P3_0003', 'BA_P3_0056', 'BA_P3_0124', 'BA_P3_0140', 'BA_P3_0154', 'BA_P3_0161', 'BA_P3_0170', 'BA_P3_0171', 'BA_P3_0172', 'BA_P3_0175', 'BA_P3_0191', 'BA_P3_0216', 'BA_P3_0251', 'BA_P3_0262', 'BA_P3_ADD_0006', 'BA_P3_ADD_0016', 'BA_P3_ADD_0017', 'BA_P3_ADD_0018', 'BA_P3_ADD_0019', 'BA_P3_ADD_0020', 'BA_P3_ADD_0036', 'BA_P3_ADD_0037', 'BA_P3_ADD_0038', 'BA_P3_ADD_0039', 'BA_P3_ADD_0040', 'BA_P3_ADD_0090', 'BA_P3_ADD_0091')
  and qa_status not like 'rejected%';

update public.brainactive_questions
set explanation = 'Shift each letter forward by 2 (A goes to C). BOX becomes DQZ, then reverse to get ZQD.', updated_at = now()
where id = 'BA_P3_0533';

update public.brainactive_questions
set explanation = 'Shift each letter forward by 1 (A goes to B). CAT becomes DBU, then reverse to get UBD.', updated_at = now()
where id = 'BA_P3_0549';

update public.brainactive_questions
set explanation = 'Shift each letter forward by 2 (A goes to C). CAT becomes ECV, then reverse to get VCE.', updated_at = now()
where id = 'BA_P3_0552';

update public.brainactive_questions
set explanation = 'Shift each letter forward by 2 (A goes to C). MAP becomes OCR, then reverse to get RCO.', updated_at = now()
where id = 'BA_P3_0553';

update public.brainactive_questions
set explanation = 'Shift each letter forward by 2 (A goes to C). RED becomes TGF, then reverse to get FGT.', updated_at = now()
where id = 'BA_P3_0571';

update public.brainactive_questions
set explanation = 'Shift each letter forward by 3 (A goes to D). RED becomes UHG, then reverse to get GHU.', updated_at = now()
where id = 'BA_P3_0582';

update public.brainactive_questions
set explanation = 'Shift each letter forward by 1 (A goes to B). MAP becomes NBQ, then reverse to get QBN.', updated_at = now()
where id = 'BA_P3_0659';

update public.brainactive_questions
set explanation = 'Numbers greater than 50 get a red tag. 28 has no red tag, so 28 cannot be greater than 50.', updated_at = now()
where id = 'BA_P3_G112';

update public.brainactive_questions
set explanation = 'Dog, cat and fish are all animals. A book is not an animal, so book is the odd one out.', updated_at = now()
where id = 'BA_P3_0323';


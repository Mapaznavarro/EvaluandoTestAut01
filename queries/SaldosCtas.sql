select EntPar.codigo, EntAdm.rut, EntPar.Nombre, EntPar.Apellidos , fon.fondo, fon.planes, par.secuencia, par.regimen_tributario, Cta.codigo,   sal.participaciones SaldoCuota from 
                 PAR_SALDOS Sal
               , cuentas_tit Cta 
               , cuentas_par Par
               , cuentas_FON Fon
               , Entidades_ADM EntAdm
               , Entidades   Ent
               , Entidades   EntPar
where Ent.Codigo = Cta.Codigo
and   Par.Codigo = Cta.codigo
and   Sal.cuenta = Cta.Codigo
and   Fon.Cuenta = Cta.Codigo
and   Sal.participaciones<> 0
-- and   Cta.titular = 1666859
-- and   EntAdm.rut = 15664514
--and Cta.Codigo = 87962713
and   EntPar.codigo = Cta.titular
and   EntAdm.codigo = EntPar.codigo
-- and   fon.planes = 3002
--and par.regimen_tributario <> 'A'
--order by sal.participaciones 
;

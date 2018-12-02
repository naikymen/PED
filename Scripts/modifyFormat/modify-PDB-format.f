      IMPLICIT NONE

      integer readstring
      integer i,slen,flen,long,j,k,m
      integer icont,icontTER,icontCHA
      character*1000 card

      
      icont=0
      icontCHA=0
      icontTER=0
      open(49,file='sab_pdb')
      open(50,file='dat_pdbs')
      open(51,file='xyz_pdbs')
      open(59,file='cha_pdbs')
     
      do while (readstring(5,card,slen).ge.0 )
         long=slen
         if(card(1:4).eq.'ATOM') then
c|AAAAAABBBBB CCCCDEEE FGGGGH   IIIIIIIIJJJJJJJJKKKKKKKKLLLLLLMMMMMM          NNOO
c|         1         2         3         4         5         6         7         8
c|12345678901234567890123456789012345678901234567890123456789012345678901234567890
c|ATOM      4  CA  ALA     1      18.685  -9.345  55.248                       C
c|ATOM      2  CA  LEU A   1     107.125  21.792  60.131  0.00  0.00           C
           write(49,110) card(1:4)
           write(50,111) card(1:26)
           write(51,112) card(31:80)
           icont=icont+1
           if(card(22:22).ne.' ') then
             write(59,119) card(22:22)
             icontCHA=icontCHA+1
           endif
         elseif(card(1:4).eq.'TER ') then
           write(49,110) card(1:4)
           write(50,111) card(1:26)
           write(51,110) card(1:4)
             icont=icont+1
             icontTER=icontTER+1 
c|MASTER        1    0    0    0    0    0    0    0 1272    0    0    0
         elseif(card(1:4).eq.'MAST') then
           write(49,110) card(1:4)
           write(50,120) card(1:80)
           write(51,110) card(1:4)
             icont=icont+1
         elseif(card(1:6).eq.'HETATM') then
c|HETATM 1814  S   DMS A 201      24.610  19.854  47.132  1.00 50.73           S
c|HETATM 4154  CAEA3MI D 128      -0.058   0.382 -30.131  0.25 17.22           C
           write(49,110) card(1:4)
           write(50,120) card(1:80)
           write(51,110) card(1:4)
             icont=icont+1
         elseif(card(1:6).eq.'CONECT') then
c|CONECT  685  684  686  688  697          
           write(49,110) card(1:4)
           write(50,121) card(1:36)
           write(51,110) card(1:4)
             icont=icont+1

         elseif(card(1:6).ne.'ATOM  '.and.
     &card(1:6).ne.'TER   '.and.
     &card(1:6).ne.'MAST  '.and.
     &card(1:6).ne.'HETATM'.and.
     &card(1:6).ne.'CONECT') then
c|HEADER
c|HELIX    2   2 GLU     47  LEU     50  1                                   4
           write(49,110) card(1:4)
           write(50,120) card(1:80)
           write(51,110) card(1:4)
             icont=icont+1
         endif
      enddo
      write(31,*) icont

      close(49)
      close(50)
      close(51)
      close(59)

      call calculo(icont,icontCHA,icontTER)

110   FORMAT(A4)
111   FORMAT(A26)
112   FORMAT(A50)
119   FORMAT(A1)
120   FORMAT(A80)
121   FORMAT(A36)
      stop
      end

C Fin del programa principal
C**************************************
C Subroutine calculo

      subroutine calculo(icont,icontCHA,icontTER)
      integer ifail,ii
      integer i,icont,icontHET,slen,flen,long,j,k,m
      integer icontCHA,b
      parameter(icontmax=10000)
c      double precision xx(icontmax)
      double precision r(icontmax,3),bfactor(icontmax)
      integer num(icontmax),naa(icontmax)
      character*7 letras(icontmax)
      character*3 aa(icontmax)
      character*4 atom(icontmax)
      character*1 cha(icontmax)
      character*10 model
      integer nnm
      character*26 xx(icontmax),ter_line(icontmax)
      character*80 hetatm(icontmax),het_line(icontmax)
      character*80 master_line(icontmax),conect_line(icontmax)
      character*80 header_line(icontmax)
      character*4 sab(icontmax),sab2(icontmax)


      open(54,file='num-model')
c|MODEL 1
      read(54,*) model,nnm
      close(54)

c|AAAAAABBBBB CCCCDEEE FGGGGH   IIIIIIIIJJJJJJJJKKKKKKKKLLLLLLMMMMMM          NNOO
c|         1         2         3         4         5         6         7         8
c|12345678901234567890123456789012345678901234567890123456789012345678901234567890
c|ATOM      3  N   ALA     1      20.046  -9.461  54.731                       N
c|ATOM      4  CA  ALA     1      18.685  -9.345  55.248                       C
c|ATOM      1  N   LEU A   1     108.374  22.191  59.501  0.00  0.00           N
c|ATOM      2  CA  LEU A   1     107.125  21.792  60.131  0.00  0.00           C

      open(50,file='dat_pdbs')
      open(51,file='xyz_pdbs')
      open(49,file='sab_pdb')

      do i=1,icont
        read(49,110) sab(i)
      enddo

      do i=1,icont
        if( sab(i).eq.'ATOM' ) then
          if ( icontCHA.ne.0 ) then
c           CON CADENA ######      
            read(50,*) letras(i),num(i),atom(i),aa(i),cha(i),naa(i)
          elseif ( icontCHA.eq.0 ) then
c           SIN CADENA ######
            read(50,*) letras(i),num(i),atom(i),aa(i),naa(i) 
            cha(i)=' '
          endif
            read(51,113) r(i,1),r(i,2),r(i,3),xx(i)

        elseif( sab(i).eq.'TER ' ) then
            read(50,111) ter_line(i)
            read(51,110) sab2(i)

        elseif( sab(i).eq.'MAST' ) then
            read(50,120) master_line(i)
            read(51,110) sab2(i)            

        elseif( sab(i).eq.'HETA' ) then
            read(50,120) het_line(i)
            read(51,110) sab2(i)

        elseif( sab(i).eq.'CONE' ) then
            read(50,121) conect_line(i)
            read(51,110) sab2(i)            

        elseif( sab(i).ne.'ATOM'.and. 
     &sab(i).ne.'TER '.and.
     &sab(i).ne.'MAST'.and.
     &sab(i).ne.'HETA'.and.
     &sab(i).ne.'CONE' ) then
            read(50,120) header_line(i)
            read(51,110) sab2(i)
        endif
      enddo 

      close(49)
      close(50)
      close(51)

      b=0
      open(52,file='ped_pdbs_modifie')

      do i=1,icont
        if( sab(i).eq.'ATOM' ) then
          if ( b.eq.0 ) then
            write(52,116) model,nnm
            b=b+1
          endif  
          if (
     &atom(i).eq.'HD11'.or.atom(i).eq.'HE11'.or.
     &atom(i).eq.'HG11'.or.atom(i).eq.'HH11'.or.
     &atom(i).eq.'HD12'.or.atom(i).eq.'HE12'.or.
     &atom(i).eq.'HG12'.or.atom(i).eq.'HH12'.or.
     &atom(i).eq.'HD13'.or.atom(i).eq.'HE13'.or.
     &atom(i).eq.'HG13'.or.atom(i).eq.'HH13'.or.
     &atom(i).eq.'HD21'.or.atom(i).eq.'HE21'.or.
     &atom(i).eq.'HG21'.or.atom(i).eq.'HH21'.or.
     &atom(i).eq.'HD22'.or.atom(i).eq.'HE22'.or.
     &atom(i).eq.'HG22'.or.atom(i).eq.'HH22'.or.
     &atom(i).eq.'HD23'.or.atom(i).eq.'HE23'.or.
     &atom(i).eq.'HG23'.or.atom(i).eq.'HH23'.or.
     &atom(i).eq.'1HA'.or.atom(i).eq.'1HB'.or.
     &atom(i).eq.'1HD'.or.atom(i).eq.'1HE'.or.
     &atom(i).eq.'1HG'.or.atom(i).eq.'1HH'.or.
     &atom(i).eq.'1HT'.or.atom(i).eq.'1HZ'.or.
     &atom(i).eq.'2HA'.or.atom(i).eq.'2HB'.or.
     &atom(i).eq.'2HD'.or.atom(i).eq.'2HE'.or.
     &atom(i).eq.'2HG'.or.atom(i).eq.'2HH'.or.
     &atom(i).eq.'2HT'.or.atom(i).eq.'2HZ'.or.
     &atom(i).eq.'3HA'.or.atom(i).eq.'3HB'.or.
     &atom(i).eq.'3HD'.or.atom(i).eq.'3HE'.or.
     $atom(i).eq.'3HG'.or.atom(i).eq.'3HH'.or.
     &atom(i).eq.'3HT'.or.atom(i).eq.'3HZ'.or.
     &atom(i).eq.'1HD1'.or.atom(i).eq.'1HD2'.or.
     &atom(i).eq.'1HE1'.or.atom(i).eq.'1HE2'.or.
     &atom(i).eq.'1HG1'.or.atom(i).eq.'1HG2'.or.
     &atom(i).eq.'1HH1'.or.atom(i).eq.'1HH2'.or.
     &atom(i).eq.'2HD1'.or.atom(i).eq.'2HD2'.or.
     &atom(i).eq.'2HE1'.or.atom(i).eq.'2HE2'.or.
     &atom(i).eq.'2HG1'.or.atom(i).eq.'2HG2'.or.
     &atom(i).eq.'2HH1'.or.atom(i).eq.'2HH2'.or.
     &atom(i).eq.'3HD1'.or.atom(i).eq.'3HD2'.or.
     &atom(i).eq.'3HG1'.or.atom(i).eq.'3HG2'
     &) then
          write(52,115) letras(i),num(i),atom(i),aa(i),cha(i),naa(i),
     &r(i,1),r(i,2),r(i,3),xx(i)
          elseif (
     &atom(i).ne.'HD11'.and.atom(i).ne.'HE11'.and.
     &atom(i).ne.'HG11'.and.atom(i).ne.'HH11'.and.
     &atom(i).ne.'HD12'.and.atom(i).ne.'HE12'.and.
     &atom(i).ne.'HG12'.and.atom(i).ne.'HH12'.and.
     &atom(i).ne.'HD13'.and.atom(i).ne.'HE13'.and.
     &atom(i).ne.'HG13'.and.atom(i).ne.'HH13'.and.
     &atom(i).ne.'HD21'.and.atom(i).ne.'HE21'.and.
     &atom(i).ne.'HG21'.and.atom(i).ne.'HH21'.and.
     &atom(i).ne.'HD22'.and.atom(i).ne.'HE22'.and.
     &atom(i).ne.'HG22'.and.atom(i).ne.'HH22'.and.
     &atom(i).ne.'HD23'.and.atom(i).ne.'HE23'.and.
     &atom(i).ne.'HG23'.and.atom(i).ne.'HH23'.and.
     &atom(i).ne.'1HA'.and.atom(i).ne.'1HB'.and.
     &atom(i).ne.'1HD'.and.atom(i).ne.'1HE'.and.
     &atom(i).ne.'1HG'.and.atom(i).ne.'1HH'.and.
     &atom(i).ne.'1HT'.and.atom(i).ne.'1HZ'.and.
     &atom(i).ne.'2HA'.and.atom(i).ne.'2HB'.and.
     &atom(i).ne.'2HD'.and.atom(i).ne.'2HE'.and.
     &atom(i).ne.'2HG'.and.atom(i).ne.'2HH'.and.
     &atom(i).ne.'2HT'.and.atom(i).ne.'2HZ'.and.
     &atom(i).ne.'3HA'.and.atom(i).ne.'3HB'.and.
     &atom(i).ne.'3HD'.and.atom(i).ne.'3HE'.and.
     &atom(i).ne.'3HG'.and.atom(i).ne.'3HH'.and.
     &atom(i).ne.'3HT'.and.atom(i).ne.'3HZ'.and.
     &atom(i).ne.'1HD1'.and.atom(i).ne.'1HD2'.and.
     &atom(i).ne.'1HE1'.and.atom(i).ne.'1HE2'.and.
     &atom(i).ne.'1HG1'.and.atom(i).ne.'1HG2'.and.
     &atom(i).ne.'1HH1'.and.atom(i).ne.'1HH2'.and.
     &atom(i).ne.'2HD1'.and.atom(i).ne.'2HD2'.and.
     &atom(i).ne.'2HE1'.and.atom(i).ne.'2HE2'.and.
     &atom(i).ne.'2HG1'.and.atom(i).ne.'2HG2'.and.
     &atom(i).ne.'2HH1'.and.atom(i).ne.'2HH2'.and.
     &atom(i).ne.'3HD1'.and.atom(i).ne.'3HD2'.and.
     &atom(i).ne.'3HG1'.and.atom(i).ne.'3HG2'
     &) then
          write(52,114) letras(i),num(i),atom(i),aa(i),cha(i),naa(i),
     &r(i,1),r(i,2),r(i,3),xx(i)
          endif

        elseif( sab(i).eq.'TER ' ) then
          write(52,111) ter_line(i)
        elseif( sab(i).eq.'MAST' ) then
          write(52,120) master_line(i)
        elseif( sab(i).eq.'HETA' ) then
          write(52,120) het_line(i)
        elseif( sab(i).eq.'CONE' ) then
          write(52,121) conect_line(i)
        elseif( sab(i).ne.'MODE'.and.
     &sab(i).ne.'ATOM'.and.
     &sab(i).ne.'TER '.and.
     &sab(i).ne.'MAST'.and.
     &sab(i).ne.'HETA'.and.
     &sab(i).ne.'CONE'.and.
     &sab(i).ne.'END ' ) then
          write(52,120) header_line(i)
        endif
      enddo
         
         if( sab(icont).ne.'TER '.and.
     &sab(icont).ne.'MAST'.and.
     &sab(icont).ne.'CONE'.and.
     &sab(icont).ne.'ENDM'.or.
     &sab(icont).eq.'END ' ) write(52,117) 'TER'
         if( sab(icont).ne.'ENDM'.or. 
     &sab(icont).eq.'END ' ) write(52,118) 'ENDMDL'

      close(52)

110   FORMAT(A4)
111   FORMAT(A26)
c|ATOM     28  SD  MET A  13      21.240  35.500  31.117  1.00 25.34
c|ATOM     29  CE  MET A  13      20.280  36.966  30.744  1.00 25.48
113   FORMAT(3(F8.3),A26)
c|AAAAAABBBBB CCCCDEEE FGGGGH   IIIIIIIIJJJJJJJJKKKKKKKKLLLLLLMMMMMM          NNOO
c|         1         2         3         4         5         6         7         8
c|12345678901234567890123456789012345678901234567890123456789012345678901234567890
c|ATOM      4  CA  ALA     1      18.685  -9.345  55.248                       C
c|ATOM      2  CA  LEU A   1     107.125  21.792  60.131  0.00  0.00           C
114   FORMAT(A7,I4,2X,A3,1x,A3,1x,A1,I4,4x,3(F8.3),A26)
115   FORMAT(A7,I4,1X,A4,1x,A3,1x,A1,I4,4x,3(F8.3),A26)
116   FORMAT(A9,I5)
117   FORMAT(A3)
118   FORMAT(A6)      
120   FORMAT(A80)
121   FORMAT(A36)
      return
      end

c------ SUBROUTINES

      integer function readstring(file,card,flen)
      integer       file, flen
      character*1000 card
      if(file.gt.200)STOP'ERROR: file number too large'
      read(file,'(a)',err=100,end=100)card
      flen=1000
      do while(card(flen:flen).eq.' ')
         flen=flen-1
      enddo
      readstring=flen
      return
 100  readstring=-1

      return
      end

